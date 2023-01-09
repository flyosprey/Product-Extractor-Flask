import re
import logging
from datetime import datetime
import scrapy
from scrapy.crawler import CrawlerProcess
from incense.spiders.init_spider import get_headers


class ZamorskiepodarkiSpider(scrapy.Spider):
    name = "zamorskiepodarki"
    allowed_domains = ["zamorskiepodarki.com"]
    start_urls = []

    def __init__(self, url_to_parse="", user_id=None, **kwargs):
        self.headers = get_headers()
        self.start_urls.append(url_to_parse)
        self.user_id = user_id
        if not self.user_id:
            raise Exception("user_id is None in scrape")
        super().__init__(**kwargs)
        self.images, self.pages, self.image_index = {"images": []}, None, None

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response, **kwargs):
        products = response.xpath("//div[@class='product-layout product-grid']")
        logging.debug("FIRST - %s", self.images)
        for product in products:
            logging.debug("URL - %s", response.url)
            product_link = product.xpath("div[@class='product-thumb']//div[@class='image']/a/@href").get()
            yield scrapy.Request(url=product_link, headers=self.headers, callback=self._get_image)
        next_page_url = self._next_page_url(response)
        if next_page_url:
            yield scrapy.Request(url=next_page_url, headers=self.headers, callback=self.parse)

    def _extract_images_link(self, response):
        products = response.xpath("//div[@class='product-layout product-grid']")
        for product in products:
            product_link = product.xpath("div[@class='product-thumb']//div[@class='image']/a/@href").get()
            yield scrapy.Request(url=product_link, headers=self.headers, callback=self._get_image)

    @staticmethod
    def _next_page_url(response) -> str or None:
        url = None
        next_pages_tag = response.xpath("//ul[@class='pagination']//li[@class='active']/following-sibling::li")
        next_pages_text = next_pages_tag.xpath("./a/text()").get()
        if next_pages_text and next_pages_text.isdigit():
            url = next_pages_tag.xpath("./a/@href").get()
        return url

    def _get_image(self, response):
        prices_data = self._get_prices_data(response)
        general_product_data = self._get_general_product_data(response)
        logging.debug("IMAGE SHOULD BE DOWNLOADED")
        incense_item = {"user_id": self.user_id, **general_product_data, **prices_data}
        yield incense_item

    @staticmethod
    def _get_general_product_data(response) -> dict:
        deep_link, date_of_parsing, status = response.url, datetime.now(), "NEW"
        category_name = \
            response.xpath("//ul[@class='breadcrumb']//li[@itemprop='itemListElement']//span/text()")[-1].get()
        image_link = response.xpath("//a[@class='thumbnail']/@href").get()
        title = response.xpath("//a[@class='thumbnail']/@title").get()
        title = title.replace("(", "").replace(")", "").replace("'", "`")
        general_product_data = {"deep_link": deep_link, "date_of_parsing": date_of_parsing, "status": status,
                                "image_link": image_link, "title": title, "category_name": category_name.strip()}
        return general_product_data

    @staticmethod
    def _get_prices_data(response) -> dict:
        product_div = response.xpath("//div[@id='product']")
        currency = product_div.xpath("..//meta[@itemprop='priceCurrency']//@content").get()
        opt_price = product_div.xpath("..//span[@class='price-new price-opt-new']/b//text()").get()
        opt_price = float(re.search(r"\d+.\d+", opt_price)[0])
        drop_price = round(opt_price * 1.1, 2)
        retail_price = product_div.xpath("..//div[@class='price-detached price-retail']/span//text()").get()
        retail_price = float(re.search(r"\d+.\d+", retail_price)[0])
        prices_data = {"opt_price": opt_price, "drop_price": drop_price, "retail_price": retail_price,
                       "currency": currency}
        return prices_data


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ZamorskiepodarkiSpider)
    process.start()
