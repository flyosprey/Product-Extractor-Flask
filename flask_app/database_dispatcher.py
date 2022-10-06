import logging
import psycopg2
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE


class DatabaseDispatcher:
    INT_TYPE_FIELDS = ('price_from', 'price_till', 'date_period_hours', 'date_period_days', 'limit')

    def get_exist_data(self, filters):
        where_query_part, limit = self._build_where_query_part(filters)
        full_query = self._build_full_query(where_query_part, limit)
        return 1

    def get_extracted_data(self, limit):
        query = "SELECT * FROM incense_flask_dev ORDER BY date_of_parsing DESC LIMIT %s" % limit
        result = self._get_data(query)
        return result

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
    def _get_data(query):
        connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        cur = connection.cursor()
        logging.debug("CONNECTED TO DB")
        cur.execute(query)
        result = cur.fetchall()
        return result
