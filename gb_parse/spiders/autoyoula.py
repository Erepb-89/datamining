import scrapy
from urllib.parse import unquote, urljoin
import pymongo

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]
    _css_selectors = {
        "brands": "div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "car": "#serp article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
    }

    data_query = {
        "title": lambda response: response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
        "url": lambda response: response.url,
        "description": lambda response: response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first(),
        "photos": lambda response: [item.attrib.get("src") for item in
                                    response.css("figure.PhotoGallery_photo__36e_r img")],
        "specs": lambda response: [
            {
                "key": item.css("div.AdvertSpecs_label__2JHnS::text").get('text'),
                "val": item.css("div.AdvertSpecs_data__xK2Qx::text").get('text'),
            }
            for item in response.css("div.AdvertCard_specs__2FEHc div.AdvertSpecs_row__ljPcX")
        ],
        "price": lambda response:
        float(response.css(".AdvertCard_price__3dDCr::text").extract_first().replace("\u2009", "")),
        "author": lambda response: AutoyoulaSpider.get_author(response)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient("mongodb://localhost:27017")

    def _get_follow(self, response, selector_css, callback, **kwargs):
        for link_selector in response.css(selector_css):
            yield response.follow(link_selector.attrib.get("href"), callback=callback)

    def parse(self, response, **kwargs):
        yield from self._get_follow(response, self._css_selectors["brands"], self.brand_parse)

    def brand_parse(self, response):
        yield from self._get_follow(response, self._css_selectors["pagination"], self.brand_parse)
        yield from self._get_follow(response, self._css_selectors["car"], self.car_parse)

    def car_parse(self, response):
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        self.db_client["gb_parse_autoyoula"][self.name].insert_one(data)

    @staticmethod
    def get_author(response):
        scripts = response.css("script::text").extract()
        for script in scripts:
            try:
                if "youlaProfile" in unquote(script):
                    author = unquote(script).split("youlaProfile")[1].split('youlaId')[1][3:27]
                    result = f"https://youla.ru/user/{author}?_ga=2.61825519.274446473.1618422702-2019711227.1618422702"
                    return (result if result else None)
            except TypeError:
                pass

