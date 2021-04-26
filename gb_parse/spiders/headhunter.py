import scrapy


class HeadHunterSpider(scrapy.Spider):
    name = "headhunter"
    allowed_domains = ["kazan.hh.ru"]
    start_urls = ["https://kazan.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    _xpath_selectors = {
        "pagination": "//a[@data-qa='pager-next']/@href",
        "vacancy": "/html/body//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "author": "//a[@data-qa='vacancy-serp__vacancy-employer']/@href",
    }

    _xpath_data_query = {
        "title": "//a[@data-qa='vacancy-serp__vacancy-title']/text()",
        "salary": "//p[@class='vacancy-salary']/span/text()",
        "description": "//div[@data-qa='vacancy-description']//text()",
        "skills": "//span[@data-qa='bloko-tag__text']/text()",
        "author": "//a[@data-qa='vacancy-serp__vacancy-employer']/@href",
    }

    _author_data_query = {
        "author_title": "//span[@data-qa='company-header-title-name']/text()",
        "author_site": "//a[@data-qa='sidebar-company-site']/@href",
        "author_emphasis": "//div[text()='Сферы деятельности']/../../div/p/text()",
        "author_description": "//div[@data-qa='company-description-text']//p/text()",
    }

    def _get_follow_xpath(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["pagination"], self.parse,
        )
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = HeadHunterLoader(response=response)
        loader.add_value("vacancy_url", response.url)
        loader.add_value("table", "vacancy_table")
        for key, selector in self._xpath_data_query.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

        yield from self._get_follow_xpath(
            response, self._xpath_selectors["author"], self.author_parse,
        )

    def author_parse(self, response):
        author_loader = HhAuthorLoader(response=response)
        author_loader.add_value("author_url", response.url)
        author_loader.add_value("table", "author_table")
        for key, selector in self._author_data_query.items():
            author_loader.add_xpath(key, selector)
        yield author_loader.load_item()
