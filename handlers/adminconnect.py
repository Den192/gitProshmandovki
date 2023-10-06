from aiogram.types import Message
from aiogram import Router, Bot , types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo import MongoClient

class MessageAnswerState(StatesGroup):
    startsendmessage = State()
    messagewait = State()


adminconnect_router = Router()
bot = Bot(token="6390983781:AAF5Jxq5RQJbePhGPg19jxF1r9oxbHP2Nm0")
mongo = MongoClient()
db = mongo.ProshmandovkiTgBot
user_id_collection=db.users
awaitmessage = db.awaitmessage
blacklist = db.blacklist

@adminconnect_router.message(Command('connect'))
@adminconnect_router.message(F.text.lower()=="связаться с администрацией")
async def AdminConnect(message:types.Message,state:FSMContext):
    await state.set_state(MessageAnswerState.startsendmessage)
    await message.answer("Отправьте текст сообщения и ожидайте ответа: ")
    awaitmessage.insert_one({'UserId':message.from_user.id, 'MessageText':message.text, 'AdminToAnswer':None})

@adminconnect_router.message(F.text, MessageAnswerState.startsendmessage)
async def MessageAwait(message:types.Message,state:FSMContext):
    useridindb = list(awaitmessage.find({'username': message.text}))
    iduser = useridindb[0]["_id"]
    result = awaitmessage.find_one({"AdminToAnswer"})
    if result is None:
        await message.answer(f"Пользователь {message.text} был забанен.",reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(f"Пользователь {message.text} уже забанен!!!",reply_markup=types.ReplyKeyboardRemove())
