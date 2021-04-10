import typing
import requests
import bs4
from urllib.parse import urljoin
from database.database import Database


class GbBlogParse:
    def __init__(self, start_url, db):
        self.db = db
        self.start_url = start_url
        self.tasks = []
        self.done_urls = set()

    def get_task(self, url, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url not in self.done_urls:
            self.done_urls.add(url)
            return task

        return lambda: None

    def _get_response(self, url) -> requests.Response:
        return requests.get(url)

    def _get_soup(self, url) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(self._get_response(url).text, "lxml")

    def parse_feed(self, url, soup):
        pag_ul = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_urls = set(
            urljoin(url, pag_a.attrs["href"])
            for pag_a in pag_ul.find_all("a")
            if pag_a.attrs.get("href")
        )
        for pag_url in pag_urls:
            self.tasks.append(self.get_task(pag_url, self.parse_feed))

        posts = set(
            urljoin(url, post_a.attrs["href"])
            for post_a in soup.find_all("a", attrs={"class": "post-item__title"})
            if post_a.attrs.get("href")
        )
        for post_url in posts:
            self.tasks.append(self.get_task(post_url, self.parse_post))

    def parse_post(self, url, soup):
        data = {
            "post_data": {
                "url": url,
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
            },
            "author_data": {
                "url": urljoin(
                    url, soup.find("div", attrs={"itemprop": "author"}).parent.attrs.get("href")
                ),
                "name": soup.find("div", attrs={"itemprop": "author"}).text,
            },
            "tags_data": [
                {"url": urljoin(url, tag.attrs.get("href")), "name": tag.text}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    def _get_comments(self, post_id):
        comment_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, comment_path))
        data = response.json()
        return data

    def run(self):
        self.tasks.append(self.get_task(self.start_url, self.parse_feed))
        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)

    def save(self, data):
        self.db.create_post(data)


if __name__ == "__main__":
    db = Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", db)
    parser.run()
