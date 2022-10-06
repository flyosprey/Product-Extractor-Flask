import time
import crochet
import psycopg2
import logging
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE
from models import SaveData
from flask import request, render_template, redirect, make_response
from flask_restful import Resource
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerRunner
from incense.spiders.zamorskiepodarki import ZamorskiepodarkiSpider
from flask_app.settings import app, api

crochet.setup()
crawl_runner = CrawlerRunner()

global scrape_complete


class MainPage(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("home_page.html"), 200, headers)

    def post(self):
        url_to_parse = request.form.get('url')
        if url_to_parse:
            result = ScrapySide().parse_data(url_to_parse)
            return make_response(render_template("home_page.html", result=result), 200, {'Content-Type': 'text/html'})
        else:
            return redirect("http://127.0.0.1:5000/parse?url_to_parse=" + url_to_parse)


class ScrapySide:
    def __init__(self):
        self.scrape_complete, self.number_of_items = False, 0

    def parse_data(self, url_to_parse):
        self.scrape_with_crochet(url_to_parse=url_to_parse)
        while self.scrape_complete is False:
            time.sleep(5)
        result = self._get_parsed_data()
        return result

    def _get_parsed_data(self):
        connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        cur = connection.cursor()
        logging.debug("CONNECTED TO DB")
        cur.execute("SELECT * FROM incense_flask_dev1 ORDER BY date_of_parsing DESC LIMIT %s" % self.number_of_items)
        result = cur.fetchall()
        return result

    def crawler_result(self, item):
        self.number_of_items += 1
        SaveData().process_item(item)

    @crochet.run_in_reactor
    def scrape_with_crochet(self, url_to_parse):
        dispatcher.connect(self.crawler_result, signal=signals.item_scraped)
        eventual = crawl_runner.crawl(ZamorskiepodarkiSpider, url_to_parse=url_to_parse)
        eventual.addCallback(self.finished_scrape)
        return eventual

    def finished_scrape(self, *args, **kwargs):
        self.scrape_complete = True


api.add_resource(MainPage, "/incense")


if __name__ == "__main__":
    app.run(debug=True)
