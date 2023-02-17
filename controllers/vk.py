import datetime

from vk_api import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class VK:
    """Создание подключения с ВК и работа с ним"""
    __USER_FOUND_COUNT = 1000
    __INPUT_AGE_MESSAGE = "Какой возраст мне искать?"
    __INPUT_CITY_MESSAGE = "В каком городе?"
    __INPUT_SEX_MESSAGE = "Какой пол ищем? (мужской/женский)"
    __INPUT_RELATION_MESSAGE = """С каким семейным положением? Возможные значения:
        1 — не женат (не замужем);
        2 — встречается;
        3 — помолвлен(-а);
        4 — женат (замужем);
        5 — всё сложно;
        6 — в активном поиске;
        7 — влюблен(-а);
        8 — в гражданском браке."""

    __long_poll = None
    __group_api = None
    __user_api = None

    def __init__(self, config):
        group_token = config.get_group_token()
        user_token = config.get_user_token()
        group_session = vk_api.VkApi(token=group_token)
        user_session = vk_api.VkApi(token=user_token)

        self.__group_api = group_session.get_api()
        self.__user_api = user_session.get_api()
        self.__long_poll = VkLongPoll(group_session)

    def send(self, user_id, message):
        self.__group_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=0,
        )

    def get_user_name(self, user_id):
        user = self.__group_api.users.get(user_id=user_id)
        name = user[0]['first_name']
        return name

    def get_long_poll(self):
        return self.__long_poll

    def get_user_photos(self, user_id):
        photos = []
        like_photo_map = dict()

        response = self.__user_api.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1,
            count=30
        )

        for item in response['items']:
            photo_id = str(item["id"])
            likes = item["likes"]

            if likes["count"]:
                likes = likes["count"]
                like_photo_map[likes] = photo_id

        list_of_ids = sorted(like_photo_map.items(), reverse=True)
        photo_ids = []
        for item in list_of_ids:
            photo_ids.append(item[1])
        try:
            photos.append(f'photo{user_id}_{photo_ids[0]}')
            photos.append(f'photo{user_id}_{photo_ids[1]}')
            photos.append(f'photo{user_id}_{photo_ids[2]}')
            return photos
        except IndexError:
            photos.append(f'photo{user_id}_{photo_ids[0]}')
            return photos

    def get_search_filter(self, user_id):
        age = self.__get_user_input(user_id, self.__INPUT_AGE_MESSAGE)
        city = self.__get_user_input(user_id, self.__INPUT_CITY_MESSAGE)
        sex = self.__get_user_input(user_id, self.__INPUT_SEX_MESSAGE)
        if sex.lower() == "мужской":
            sex = 2
        else:
            sex = 1
        relation = self.__get_user_input(user_id, self.__INPUT_RELATION_MESSAGE)

        return {
            "age": age,
            "city": city,
            "sex": sex,
            "relation": relation,
        }

    def __get_user_input(self, user_id, message):
        self.send(user_id, message)
        for event in self.__long_poll.listen():
            if event.type != VkEventType.MESSAGE_NEW:
                continue
            if not event.to_me:
                continue

            event_message = event.text.lower()
            event_user_id = event.user_id

            if event_user_id != user_id:
                continue

            return event_message

    def get_users(self, user_offset, search_filter):
        users = []

        response_users = self.__user_api.users.search(
            hometown=search_filter["city"],
            sex=search_filter["sex"],
            age_from=search_filter["age"],
            age_to=search_filter["age"],
            has_photo=1,
            sort=0,
            count=self.__USER_FOUND_COUNT,
            offset=user_offset,
            relation=search_filter["relation"],
            is_closed=False,
            fiels="id"
        )

        for user in response_users["items"]:
            users.append(user["id"])
        return users

    def __get_user_age(self, user_info):
        split_date = user_info["bdate"].split(".")
        date = datetime.date(int(split_date[2]), int(split_date[1]), int(split_date[0]))
        today = datetime.date.today()
        return today.year - date.year

    def send_photos(self, user_id, photos):
        self.__group_api.messages.send(
            user_id=user_id,
            random_id=0,
            attachment=",".join(photos)
        )

    def is_valid_user(self, user_id):
        user = self.__group_api.users.get(user_id=user_id)[0]
        return not user["is_closed"]
