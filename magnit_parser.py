import requests
from urllib.parse import urljoin
import bs4
import pymongo


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client["gb_data_mining_29_03_21"]
        self.collection = db["magnit"]

    def _get_response(self, url, *args, **kwargs):
        # TODO: Сделать Обработку ошибок и статусов
        return requests.get(url, *args, **kwargs)

    def _get_soup(self, url, *args, **kwargs):
        # TODO: Обработать ошибки
        return bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def _template(self):
        return {
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href", "")),
        }

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        product_tags = catalog_main.find_all("a", recursive=False)
        for product_tag in product_tags:
            product = {}
            for key, funk in self._template.items():
                # TODO: Обработать ошибки отсутсвия полей
                product[key] = funk(product_tag)
            yield product

    def _save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()

"""
for itm in collection.find({'product_name': {"$regex": r".*говяд"}}, {"url":1}):
    print(itm)
"""
