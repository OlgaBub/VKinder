from bot.bot import Bot
from configs.config import Config
from controllers.user import UserController
from controllers.vk import VK
from repositories.database import Database

CONFIG_FILE_PATH = "configs/config.ini"

config = Config(CONFIG_FILE_PATH)
database = Database(config)
user_controller = UserController(database)
vk = VK(config)
bot = Bot(user_controller, vk)

bot.run()
