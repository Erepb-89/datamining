from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join
from urllib.parse import urljoin


def authors_url(employer):
    return urljoin("https://hh.ru/", employer)


def emphasis_to_list(emphasis):
    return emphasis.split(', ')


class HeadHunterLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = Join()
    description_out = Join()
    author_in = MapCompose(authors_url)
    author_out = TakeFirst()


class HhAuthorLoader(ItemLoader):
    default_item_class = dict
    author_title_out = Join()
    author_site_out = Join()
    author_emphasis_in = MapCompose(emphasis_to_list)
    author_description_out = Join()
