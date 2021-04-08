import requests
from urllib.parse import urljoin
import bs4
import pymongo
import datetime as dt

MONTHS = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client["gb_data_mining"]
        self.collection = db["magnit"]

    def _get_response(self, url, *args, **kwargs):
        response = requests.get(url, *args, **kwargs)
        if response.status_code in (200, 301, 304):
            return response

    def _get_soup(self, url, *args, **kwargs):
        # TODO: Обработать ошибки
        return bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def _template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href", "")),
            "promo_name": lambda tag: tag.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: float(".".join(item for item in tag.find(
                        "div", attrs={"class": "label__price_old"}).text.split())),
            "new_price": lambda tag: float(".".join(item for item in tag.find(
                        "div", attrs={"class": "label__price_new"}).text.split())),
            "image_url": lambda tag: tag.find("img").attrs.get('data-src'),
            "date_from": lambda tag: self._format_date(tag.find("div", attrs={"class": "card-sale__date"}).text)[0],
            "date_to": lambda tag: self._format_date(tag.find("div", attrs={"class": "card-sale__date"}).text)[1]
        }

    def _format_date(self, source_date):
        date_list = source_date.replace("с ", "").replace("\n", "").split("до ")
        result = []
        if MONTHS[date_list[1].split()[1]] < MONTHS[date_list[0].split()[1]]:
            formatted_year = dt.datetime.now().year + 1
        else:
            formatted_year = dt.datetime.now().year

        for date in date_list:
            if date_list.index(date) == 1:
                temp_year = formatted_year
            else:
                temp_year = dt.datetime.now().year

            splitted_date = date.split()
            new_date = dt.datetime(
                year=temp_year,
                month=MONTHS[splitted_date[1]],
                day=int(splitted_date[0])
            )
            result.append(new_date)
        return result

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        product_tags = catalog_main.find_all("a", recursive=False)
        for product_tag in product_tags:
            product = {}
            for key, funk in self._template.items():
                try:
                    product[key] = funk(product_tag)
                except(AttributeError, ValueError):
                    pass
            yield product

    def _save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
