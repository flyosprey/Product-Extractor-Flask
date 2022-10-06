import psycopg2
import logging
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE


class SaveData:
    def __init__(self):
        self.connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        self.cur = self.connection.cursor()
        logging.debug("CREATING DATABASE")
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS incense_flask_dev(
                    id serial PRIMARY KEY, 
                    category_name VARCHAR(120),
                    title VARCHAR(200),
                    image_link TEXT,
                    deep_link TEXT,
                    opt_price NUMERIC,
                    drop_price NUMERIC,
                    retail_price NUMERIC,
                    currency VARCHAR(10),
                    status VARCHAR(10),
                    date_of_parsing TIMESTAMP
                )
                """)

    def process_item(self, item):
        self.cur.execute("SELECT * FROM incense_flask_dev WHERE title = '%s'" % item['title'])
        result = self.cur.fetchone()
        if result:
            logging.debug("ITEM IS ALREADY IN EXIST: '%s'" % item['title'])
            self.cur.execute("UPDATE incense_flask_dev SET status = 'OLD', "
                             "opt_price = %(opt_price)s, "
                             "drop_price = %(drop_price)s, "
                             "retail_price = %(retail_price)s, "
                             "date_of_parsing = %(date_of_parsing)s "
                             "WHERE title = '%(title)s'" % item)
        else:
            logging.debug("INSERTING ITEM")
            self.cur.execute("INSERT INTO incense_flask_dev "
                             "(category_name, title, image_link, deep_link, opt_price, drop_price, retail_price, "
                             "currency, status, date_of_parsing) VALUES ('%(category_name)s', '%(title)s', "
                             "'%(image_link)s', '%(deep_link)s', %(opt_price)s, %(drop_price)s, %(retail_price)s', "
                             "%(currency)s', '%(status)s', '%(date_of_parsing)s')" % item)
        self.connection.commit()
        self.close_spider()
        return item

    def close_spider(self):
        self.cur.close()
        self.connection.close()
