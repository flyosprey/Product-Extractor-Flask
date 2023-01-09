import logging
import psycopg2.extras
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE, PORT


class DatabaseDispatcher:
    def get_exist_data(self, filters, user_id) -> list:
        where_query_part, limit_query_part = self._build_where_and_limit_query_part(filters, user_id)
        full_query = self._build_full_query(where_query_part, limit_query_part)
        results = self._get_data(full_query)
        return results

    def get_extracted_data(self, limit, user_id) -> list:
        query = "SELECT * FROM incenses WHERE user_id=%s ORDER BY date_of_parsing DESC LIMIT %s" % (user_id, limit)
        results = self._get_data(query)
        return results

    def get_user(self, user_credentials):
        query = "SELECT * FROM users WHERE username='%(username)s' AND password='%(password)s'" % user_credentials
        user_credentials = self._get_data(query)
        if not user_credentials:
            result = {"error": {"message": "Credentials are wrong"}}
        else:
            result = {"user_id": user_credentials[0]["id"]}
        return result

    @staticmethod
    def _build_full_query(where_query_part, limit_query_part) -> str:
        full_query = "SELECT * FROM incenses %s ORDER BY date_of_parsing DESC %s" \
                     % (where_query_part, limit_query_part)
        full_query = " ".join(full_query.split())
        return full_query

    def _build_where_and_limit_query_part(self, filters, user_id) -> (str, str):
        where_query_part, like_query_part, filters, limit = "", "", {**filters}, None
        for key in filters:
            field = self._get_field(key, filters)
            if key == "limit" and filters[key]:
                limit = filters[key]
                continue
            like_query_part += "%s LIKE %s, " % (key, field) if field else ""
        like_query_part = like_query_part.rstrip(", ")
        like_query_part = " AND %s" % like_query_part if like_query_part else ""
        where_query_part = "WHERE user_id=%s%s" % (user_id, like_query_part)
        limit_query_part = "LIMIT %s" % limit if limit else ""
        return where_query_part, limit_query_part

    @staticmethod
    def _get_field(key, filters) -> str:
        field = None
        if filters[key]:
            field = f"'%{filters[key]}%'"
        return field

    @staticmethod
    def _get_data(query) -> list:
        connection = psycopg2.connect(host=HOSTNAME, password=PASSWORD, user=USERNAME, dbname=DATABASE, port=PORT)
        cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        logging.debug("CONNECTED TO DB")
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        connection.close()
        return results
