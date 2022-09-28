# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class IncensePipeline:
    def __init__(self):
        hostname = '127.0.0.1'
        username = 'vladyslav'
        password = 'Kannibal21_'
        database = 'incense'

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS incense(
                    id serial PRIMARY KEY, 
                    title TEXT,
                    image_link TEXT,
                    opt_price NUMERIC,
                    drop_price NUMERIC,
                    discount_price NUMERIC,
                    currency VARCHAR(30),
                    status VARCHAR(30)
                )
                """)

    def process_item(self, item, spider):
        self.cur.execute("select * from incense where title = '%s'" % item['title'])
        result = self.cur.fetchone()
        if result:
            spider.logger.warn("Item already in database: '%s'" % item['title'])
            self.cur.execute("UPDATE incense SET status = 'OLD' where title = '%s'" % (item['title'],))
        else:
            self.cur.execute("insert into incense (title, image_link, opt_price, drop_price, discount_price, currency) "
                             "values ('%s','%s',%s,%s,%s,'%s')" %
                             (item["title"], item["image_link"], item["opt_price"], item["drop_price"],
                              item["discount_price"], item["currency"]))
            self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
