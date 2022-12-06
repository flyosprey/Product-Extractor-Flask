import psycopg2
from psycopg2 import sql
from credentials import HOSTNAME, USERNAME, PASSWORD, DATABASE


def __initialize_model():
    connection = psycopg2.connect(host=HOSTNAME, user="postgres", password="", dbname="postgres")
    cur = connection.cursor()
    __initialize_user(cur, connection)
    __initialize_database(cur, connection)
    __initialize_privileges(cur, connection)

def __initialize_table():
    main_table_connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
    table_cursor = main_table_connection.cursor()
    create_table_query = """
            CREATE TABLE IF NOT EXISTS %s(
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
            """
    table_cursor.execute(create_table_query, TABLE)
    main_table_connection.commit()

def __initialize_user(cur, connection):
    if not __is_user_exist(cur):
        query = sql.SQL("CREATE ROLE {username} WITH PASSWORD '{password}'").format(
            username=sql.Literal(USERNAME),
            password=sql.Literal(PASSWORD),
        )
        create_user_query = "CREATE ROLE %s WITH PASSWORD '%s'"
        cur.execute(query)
        connection.commit()

def __initialize_database(cur, connection):
    if not __is_database_exist(cur):
        cur.execute('CREATE DATABASE %s', DATABASE)
        connection.commit()

def __is_user_exist(cur) -> bool:
    cur.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '%s'", USERNAME)
    is_exist = cur.fetchone()
    return is_exist

def __is_database_exist(cur) -> bool:
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s'", DATABASE)
    is_exist = cur.fetchone()
    return is_exist

def __initialize_privileges(cur, connection):
    if __is_user_exist(cur) and __is_database_exist(cur):
        grand_privileges_query = "GRANT ALL PRIVILEGES ON DATABASE %s TO %s"
        cur.execute(grand_privileges_query, (DATABASE, USERNAME))
        connection.commit()
        __initialize_table()


if __name__ == "__main__":
    __initialize_model()