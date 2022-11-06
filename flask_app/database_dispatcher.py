import logging
import psycopg2
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE


class DatabaseDispatcher:
    def get_exist_data(self, filters) -> list:
        where_query_part, limit_query_part = self._build_where_and_limit_query_part(filters)
        full_query = self._build_full_query(where_query_part, limit_query_part)
        results = self._get_data(full_query)
        return results

    def get_extracted_data(self, limit) -> list:
        query = f"SELECT * FROM incense_flask_dev ORDER BY date_of_parsing DESC LIMIT {limit}"
        results = self._get_data(query)
        return results

    def get_user_credentials(self):
        query = "SELECT * FROM incense_user"
        user_credentials = self._get_data(query)
        return user_credentials[0]

    @staticmethod
    def _build_full_query(where_query_part, limit_query_part) -> str:
        full_query = f"SELECT * FROM incense_flask_dev {where_query_part} " \
                     f"ORDER BY date_of_parsing DESC {limit_query_part}"
        full_query = " ".join(full_query.split())
        return full_query

    def _build_where_and_limit_query_part(self, filters) -> (str, str):
        where_query_part, filters, limit = "", {**filters}, None
        for key in filters:
            field = self._get_field(key, filters)
            if key == "limit" and filters[key]:
                limit = filters[key]
                continue
            where_query_part += f"{key} LIKE {field}, " if field else ""
        where_query_part = where_query_part.rstrip(", ")
        where_query_part = "WHERE " + where_query_part if where_query_part else where_query_part
        limit_query_part = f"LIMIT {limit}" if limit else ""
        return where_query_part, limit_query_part

    @staticmethod
    def _get_field(key, filters) -> str:
        field = None
        if filters[key]:
            field = f"'%{filters[key]}%'"
        return field

    @staticmethod
    def _get_data(query) -> list:
        connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
        cur = connection.cursor()
        logging.debug("CONNECTED TO DB")
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        connection.close()
        return results
