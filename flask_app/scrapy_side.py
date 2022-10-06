import crochet
import time
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerRunner
from incense.spiders.zamorskiepodarki import ZamorskiepodarkiSpider
from flask_app.database_dispatcher import DatabaseDispatcher
from models import SaveData

crochet.setup()
crawl_runner = CrawlerRunner()


class ScrapySide:
    def __init__(self):
        self.scrape_complete, self.number_of_items = False, 1

    def parse_data(self, url_to_parse):
        self.scrape_with_crochet(url_to_parse=url_to_parse)
        while self.scrape_complete is False:
            time.sleep(5)
        query = "SELECT * FROM incense_flask_dev ORDER BY date_of_parsing DESC LIMIT %s" % self.number_of_items
        result = DatabaseDispatcher().get_data(query)
        return result

    def crawler_result(self, item):
        self.number_of_items += 1
        save_obj = SaveData()
        save_obj.process_item(item)

    @crochet.run_in_reactor
    def scrape_with_crochet(self, url_to_parse):
        dispatcher.connect(self.crawler_result, signal=signals.item_scraped)
        eventual = crawl_runner.crawl(ZamorskiepodarkiSpider, url_to_parse=url_to_parse)
        eventual.addCallback(self.finished_scrape)
        return eventual

    def finished_scrape(self, *args, **kwargs):
        self.scrape_complete = True
