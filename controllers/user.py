class UserController:
    """Основные действия с людьми"""
    __database: None

    def __init__(self, database):
        self.__database = database

    def new_search(self):
        self.__database.clear_tables()

    def get_users(self):
        return self.__database.get_users()

    def is_valid_user(self, user_id):
        return not self.__database.is_showed_user(user_id)

    def show_user(self, user_id):
        self.__database.append_showed_user(user_id)

    def get_user_count(self):
        return self.__database.get_users_count()

    def append_users(self, users):
        self.__database.append_users(users)

    def set_search_filter(self, search_filter):
        self.__database.append_search_filter(search_filter)

    def get_search_filter(self):
        return self.__database.get_search_filter()

    def is_set_filter(self):
        return self.__database.is_set_filter()
