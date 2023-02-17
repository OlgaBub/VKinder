import configparser


class Config:
    """Загрузка и управление конфигурацией приложения"""
    __config = configparser.ConfigParser()

    def __init__(self, config_file_path):
        self.data = []
        self.__load_from_file(config_file_path)

    def get_group_token(self):
        return self.__config['vk']['group_token']

    def get_user_token(self):
        return self.__config['vk']['user_token']

    def get_db_host(self):
        return self.__config['db']['host']

    def get_db_user(self):
        return self.__config['db']['user']

    def get_db_password(self):
        return self.__config['db']['password']

    def get_db_port(self):
        return self.__config['db']['port']

    def get_db_name(self):
        return self.__config['db']['dbname']

    def __load_from_file(self, config_file_path):
        self.__config.read(config_file_path)
