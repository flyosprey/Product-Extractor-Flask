# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
import logging
from decouple import config


class IncensePipeline:
    def __init__(self):
        hostname = config('HOSTNAME')
        username = config('USERNAME')
        password = config('PASSWORD')
        database = config('DATABASE')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        logging.debug("CREATING DATABASE")
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS incense(
                    id serial PRIMARY KEY, 
                    title TEXT,
                    image_link TEXT,
                    deep_link TEXT,
                    opt_price NUMERIC,
                    drop_price NUMERIC,
                    discount_price NUMERIC,
                    currency VARCHAR(30),
                    status VARCHAR(30),
                    datetime VARCHAR(30)
                )
                """)

    def process_item(self, item, spider):
        self.cur.execute("SELECT * FROM incense WHERE title = '%s'" % item['title'])
        result = self.cur.fetchone()
        if result:
            logging.debug("ITEM IS ALREADY IN EXIST: '%s'" % item['title'])
            self.cur.execute("UPDATE incense SET status = 'OLD' WHERE title = '%s'" % (item['title'],))
        else:
            logging.debug("INSERTING ITEM")
            self.cur.execute("INSERT INTO incense "
                             "(title, image_link, deep_link, opt_price, drop_price, retail_price, currency, "
                             "status, datetime) VALUES ('%(title)s','%(image_link)s','%(deep_link)s',%(opt_price)s,"
                             "%(drop_price)s,%(retail_price)s,'%(currency)s','%(status)s''%(date_of_parsing)s')" % item)
            self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
