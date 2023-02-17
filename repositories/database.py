import psycopg2


class Database:
    """Соединение и работа с базой данных"""
    __SHOWED_USER_TABLE = "showed_users"
    __SEARCH_FILTER = "search_filter"
    __USERS_TABLE = "users"

    __config = None
    __cursor = None
    __conn = None

    def __init__(self, config):
        self.__config = config
        self.__connect()
        self.__init_tables()

    def __connect(self):
        self.__conn = psycopg2.connect(
            database=self.__config.get_db_name(),
            user=self.__config.get_db_user(),
            password=self.__config.get_db_password(),
            host=self.__config.get_db_host(),
            port=self.__config.get_db_port(),
        )
        self.__conn.autocommit = True
        self.__cursor = self.__conn.cursor()

    def __init_tables(self):
        self.__cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.__SHOWED_USER_TABLE} (
            "user" character varying NOT NULL)""",
        )
        self.__cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.__USERS_TABLE} (
            "user" character varying)"""
        )
        self.__cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.__SEARCH_FILTER} (
                    "id" serial,
                    "age" int NOT NULL,
                    "sex" int NOT NULL,
                    "city" character varying NOT NULL,
                    "relation" int NOT NULL)"""
        )

    def append_showed_user(self, user_id):
        self.__cursor.execute(f'INSERT INTO {self.__SHOWED_USER_TABLE} ("user") VALUES (%s)', [user_id])

    def is_showed_user(self, user_id):
        self.__cursor.execute(f'SELECT EXISTS (SELECT * FROM {self.__SHOWED_USER_TABLE} WHERE "user" = %s);', [user_id])
        row = self.__cursor.fetchone()
        return row[0]

    def append_users(self, users):
        for user in users:
            self.append_user(user)

    def append_user(self, user_id):
        self.__cursor.execute(f'INSERT INTO {self.__USERS_TABLE} ("user") VALUES (%s)', [user_id])

    def get_users(self):
        users = []
        self.__cursor.execute(f'SELECT * FROM {self.__USERS_TABLE}')
        for row in self.__cursor.fetchall():
            users.append(row[0])
        return users

    def get_users_count(self):
        self.__cursor.execute(f'SELECT count(*) FROM {self.__USERS_TABLE}')
        row = self.__cursor.fetchone()
        return row[0]

    def append_search_filter(self, search_filter):
        self.__cursor.execute(f'INSERT INTO {self.__SEARCH_FILTER} '
                              f'("age", "sex", "city", "relation") VALUES (%s, %s, %s, %s)',
                              [search_filter["age"],
                               search_filter["sex"],
                               search_filter["city"],
                               search_filter["relation"]])

    def get_search_filter(self):
        self.__cursor.execute(f'SELECT ("age", "sex", "city", "relation") FROM {self.__SEARCH_FILTER}')
        search_filter = self.__cursor.fetchone()[0]
        filter = {
            "age": search_filter[0],
            "sex": search_filter[1],
            "city": search_filter[2],
            "relation": search_filter[3],
        }
        return filter

    def is_set_filter(self):
        self.__cursor.execute(f'SELECT count(*) FROM {self.__SEARCH_FILTER}')
        count = self.__cursor.fetchone()[0]
        return count == 1

    def clear_tables(self):
        self.__conn.autocommit = True
        self.__cursor.execute(f'TRUNCATE {self.__SHOWED_USER_TABLE}, {self.__USERS_TABLE}, {self.__SEARCH_FILTER}')
