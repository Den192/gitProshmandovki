import asyncio
import logging
from typing import Any
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient
from datetime import date

from handlers import get_router
from handlers.admins import admin_router
from adminfilter import HasAdminRights
from middlewares import BlacklistMiddleware

mongo = MongoClient()
db = mongo.ProshmandovkiTgBot
user_id_collection=db.users
admin_collection = db.admins

chatId="-4056699312"
#Чат группы работающей:	-4056699312
#Чат тестовой группы: -4015760454
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6390983781:AAF5Jxq5RQJbePhGPg19jxF1r9oxbHP2Nm0")
# Диспетчер
#dp = Dispatcher(bot, storage=MemoryStorage())
#dp.middleware.setup(LoggingMiddleware())


storage=MemoryStorage()
dp=Dispatcher()

kb=[
        [
            types.KeyboardButton(text="Добавить кандидата"),
            types.KeyboardButton(text="Отправить репорт"),
            types.KeyboardButton(text="Связаться с администрацией")
        ],
    ]
keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

dp.message.outer_middleware(BlacklistMiddleware())
dp.message.filter(F.chat.type == "private")
# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    result = user_id_collection.find_one({"_id":message.from_user.id})
    if result is None:
        today = date.today()
        #user_info = [{"_id":message.from_user.id, "username":message.from_user.username,"registrationDate":today.strftime("%d-%b-%Y")}]
        user_id_collection.insert_one({"_id":message.from_user.id, "username":message.from_user.username,"registrationDate":today.strftime("%d-%b-%Y")})
        del result,today
    await message.answer("Привет! Этот бот создан для подачи кандидата в прошмандовки ФИТУ!\nДля продолжения отправь комманду /addcandidate или выбери ее через меню бота или воспользуйтесь кнопками",reply_markup=keyboard)



async def main():
    admin_router.message.filter(HasAdminRights())
    talk_router = get_router()
    dp.include_router(admin_router)
    dp.include_router(talk_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())