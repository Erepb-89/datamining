import re

import scrapy

from gb_parse.loaders import AutoyoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    _xpath_selectors = {
        "brands": "//a[@data-target='brand']/@href",
        "pagination": "//div[contains(@class, 'Paginator_block')]"
        "/a[@data-target-id='button-link-serp-paginator']/@href",
        "car": "//article[@data-target='serp-snippet']//a[@data-target='serp-snippet-title']/@href",
    }
    _xpath_data_query = {
        "title": "//div[@data-target='advert-title']/text()",
        "price": "//div[@data-target='advert-price']/text()",
        "photos": "//div[contains(@class, 'PhotoGallery_block')]//figure/picture/img/@src",
        "characteristics": "//div[contains(@class, 'AdvertCard_specs')]"
        "/div/div[contains(@class, 'AdvertSpecs_row')]",
        "description": "//div[@data-target='advert-info-descriptionFull']/text()",
        "author": '//body/script[contains(text(), "window.transitState = decodeURIComponent")]',
    }

    def _get_follow_xpath(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["brands"], self.brand_parse
        )

    def brand_parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["pagination"], self.brand_parse
        )
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["car"], self.car_parse,
        )

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._xpath_data_query.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
