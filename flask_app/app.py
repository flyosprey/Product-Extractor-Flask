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
            return {"result": "BAD REQUEST!"}, status.HTTP_400_BAD_REQUEST


class DatabaseDispatcher:
    INT_TYPE_FIELDS = ('price_from', 'price_till', 'date_period_hours', 'date_period_days', 'limit')

    def get_data_from_database(self, filters):
        where_query_part, limit = self._build_where_query_part(filters)
        full_query = self._build_full_query(where_query_part, limit)
        return 1

    @staticmethod
    def _build_full_query(where_query_part, limit):
        full_query = f"SELECT * FROM incense_flask_dev {where_query_part} ORDER BY date_of_parsing DESC LIMIT {limit}"
        full_query = " ".join(full_query.split())
        return full_query

    def _build_where_query_part(self, filters):
        where_query_part, filters, field, limit = "WHERE ", {**filters}, None, 1
        for key in filters:
            if key == 'submitbutton':
                continue
            if filters[key]:
                if key in self.INT_TYPE_FIELDS:
                    filters[key] = int(filters[key])
                field = filters[key] if isinstance(filters[key], int) else f"'{filters[key]}'"
            if key == "limit":
                limit = filters[key]
                continue
            if field:
                where_query_part += f"{key} = {field}, "
        where_query_part = where_query_part.rstrip(", ")
        where_query_part = "" if where_query_part == "WHERE" else where_query_part
        return where_query_part, limit

    @staticmethod
    def get_data(query):
        connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        cur = connection.cursor()
        logging.debug("CONNECTED TO DB")
        cur.execute(query)
        result = cur.fetchall()
        return result


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
