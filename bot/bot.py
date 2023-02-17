from vk_api.longpoll import VkEventType


class Bot:
    """Прием и обработка команд от пользователя"""
    __NEW_SEARCH_COMMAND = "начать поиск заново"
    __NEXT_COMMAND = "дальше"

    __user_controller = None
    __long_poll = None
    __vk = None

    def __init__(self, user_controller, vk):
        self.__user_controller = user_controller
        self.__vk = vk
        self.__long_poll = vk.get_long_poll()

    def run(self):
        for event in self.__long_poll.listen():
            self.__event_handler(event)

    def __event_handler(self, event):
        if event.type != VkEventType.MESSAGE_NEW:
            return
        if not event.to_me:
            return

        message = event.text.lower()
        user_id = event.user_id

        self.__message_handler(message, user_id)

    def __message_handler(self, message, user_id):
        if message == self.__NEW_SEARCH_COMMAND:
            self.__new_search(user_id)
        elif message == self.__NEXT_COMMAND:
            self.__next_command(user_id)
        else:
            self.__help_command(user_id)

    def __next_command(self, user_id):
        users = self.__user_controller.get_users()
        for user in users:
            is_valid = self.__user_controller.is_valid_user(user)
            is_vk_valid = self.__vk.is_valid_user(user)
            self.__user_controller.show_user(user)
            if not is_valid or not is_vk_valid:
                continue
            self.__send_user(user_id, user)
            return

        is_set_filter = self.__user_controller.is_set_filter()
        if not is_set_filter:
            search_filter = self.__vk.get_search_filter(user_id)
            self.__user_controller.set_search_filter(search_filter)
            append_user_count = self.__load_users(search_filter)
        else:
            search_filter = self.__user_controller.get_search_filter()
            append_user_count = self.__load_users(search_filter)

        if append_user_count == 0:
            return
        self.__next_command(user_id)

    def __send_user(self, to_user, user_id):
        photos = self.__vk.get_user_photos(user_id)
        user_url = self.__get_user_url(user_id)
        self.__vk.send_photos(to_user, photos)
        self.__vk.send(to_user, user_url)

    def __get_user_url(self, user_id):
        return f"https://vk.com/id{user_id}"

    def __load_users(self, search_filter):
        current_user_count = self.__user_controller.get_user_count()
        users = self.__vk.get_users(current_user_count, search_filter)
        self.__user_controller.append_users(users)
        return len(users)

    def __new_search(self, user_id):
        self.__user_controller.new_search()
        response_message = self.__get_new_search_message(user_id)
        self.__vk.send(user_id, response_message)

    def __get_new_search_message(self, user_id):
        user_name = self.__vk.get_user_name(user_id)
        return f"{user_name}, я успешно забыл всех, кого мы искали.\nВремя начать жизнь с чистого листа!"

    def __help_command(self, user_id):
        self.__send_help_message(user_id)

    def __send_help_message(self, user_id):
        response_message = self.__get_help_message(user_id)
        self.__vk.send(user_id, response_message)

    def __get_help_message(self, user_id):
        user_name = self.__vk.get_user_name(user_id)
        return f'''{user_name}, я вас так долго ждал! Посмотрите, что я умею:
        "{self.__NEW_SEARCH_COMMAND}" - начинаю поиск людей для вас, как будто я ничего о вас не знаю!
        "{self.__NEXT_COMMAND}" - смотреть следующего человека, возможно он и есть тот самый!'''
