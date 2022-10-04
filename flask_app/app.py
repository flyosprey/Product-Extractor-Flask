import time
import crochet
import psycopg2
import logging
import json
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE
from models import SaveData
from flask import request, render_template, redirect, url_for
from flask_restful import Resource
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerRunner
from incense.spiders.zamorskiepodarki import ZamorskiepodarkiSpider
from flask_app.settings import app, api

output_data = []
crochet.setup()
crawl_runner = CrawlerRunner()

global scrape_complete


class MainPage(Resource):
    def get(self):
        return render_template("index.html")

    def post(self):
        url_to_parse = request.form['url']
        return redirect(url_for("parse/" + url_to_parse))


class ScrapySide(Resource):
    def __init__(self):
        self.scrape_complete = False

    def get(self):
        url_to_parse = request.args.get("url_to_parse", "")
        self.scrape_with_crochet(url_to_parse=url_to_parse)
        while self.scrape_complete is False:
            time.sleep(5)
        data = self._get_parsed_data()
        data = json.dumps(data, ensure_ascii=False, default=str)
        return data

    @staticmethod
    def _get_parsed_data():
        connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        cur = connection.cursor()
        logging.debug("CONNECTED TO DB")
        cur.execute("SELECT * FROM incense_flask_dev1 ORDER BY date_of_parsing DESC LIMIT 10")
        result = cur.fetchall()
        return result

    @staticmethod
    def crawler_result(item):
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
api.add_resource(ScrapySide, "/parse")


if __name__ == "__main__":
    app.run(debug=True)
