from aiogram.types import Message
from aiogram import Router, Bot , types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo import MongoClient


admin_router = Router()
bot = Bot(token="6390983781:AAF5Jxq5RQJbePhGPg19jxF1r9oxbHP2Nm0")
mongo = MongoClient()
db = mongo.ProshmandovkiTgBot
user_id_collection=db.users
blacklist = db.blacklist

class adminstate(StatesGroup):
    startadmin=State()
    useridadmin = State()

class banstate(StatesGroup):
    startban=State()
    endban=State()

class unbanstate(StatesGroup):
    startunban=State()

def callKb():
    kb=[
        [
           types.KeyboardButton(text="Ответить пользователю"),
           types.KeyboardButton(text="Забанить"),
           types.KeyboardButton(text="Разбанить"),
           types.KeyboardButton(text="Отменить")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

def keyboardBuilder(BanUnban):
    builder = ReplyKeyboardBuilder()
    if BanUnban == True:
        cursor = user_id_collection.find({},{"_id":0,'username': 1})
    elif BanUnban == False:
        cursor = blacklist.find({},{"_id":0,'username': 1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["username"] for result in list_cursor]
    for i in range(0,len(editedcursor)):
        builder.button(text=f"{editedcursor[i]}")
    builder.adjust(3,3,3,3,3,3,3,3)
    return builder.as_markup()


@admin_router.message(Command("admin"))
async def AdminAnswer(message: types.Message):
    await message.answer("!!!Режим Администратора!!!", reply_markup=callKb())

@admin_router.message(F.text.lower()=="ответить пользователю")
async def ReportAnswer(message: types.Message, state:FSMContext):
    await state.set_state(adminstate.startadmin)
    await message.answer("Выберите пользователя, для отправления ответа",reply_markup=keyboardBuilder(True))
@admin_router.message(F.text.lower()=="отменить")
async def CancelAnswer(message: types.Message):
    await message.answer("Действие отменено, для перезапуска нажмите /admin или /start",reply_markup=types.ReplyKeyboardRemove())
def UserList():
    listuser = user_id_collection.find({},{"_id":0,'username': 1})
    listuser_cursor = [result for result in listuser]
    userlist = [result["username"] for result in listuser_cursor]
    return userlist

@admin_router.message(adminstate.startadmin, F.text!="/cancel")
async def GetUserReport(message: types.Message, state:FSMContext):
    await state.set_state(adminstate.useridadmin)
    await message.answer("Введите текст для этого пользователя:",reply_markup=types.ReplyKeyboardRemove())
    useridindb = list(user_id_collection.find({'username': message.text}))
    await state.update_data(UserId = useridindb[0]["_id"])
    del useridindb

@admin_router.message(adminstate.useridadmin, F.text!="/cancel")
async def SendUserReport(message:types.Message,state:FSMContext):
    userid = await state.get_data()
    await bot.send_message(chat_id=userid['UserId'], text="Вам пришло сообщение от администрации:\n"+message.text)
    await message.answer("Сообщение отправлено!")
    await message.answer("Для дальнейшей работы, нажмите /admin или /start")
    await state.clear()

@admin_router.message(F.text.lower()=="забанить")
async def BanUser(message:types.Message,state:FSMContext):
    await state.set_state(banstate.startban)
    await message.answer("Выберите пользователя для бана", reply_markup=keyboardBuilder(True))
@admin_router.message(banstate.startban, F.text != '/cancel')
async def UserIdBan(message: types.Message,state:FSMContext):
    useridindb = list(user_id_collection.find({'username': message.text}))
    iduser = useridindb[0]["_id"]
    result = blacklist.find_one({"id":iduser})
    if result is None:
        blacklist.insert_one({"id":iduser,"username":message.text})
        await message.answer(f"Пользователь {message.text} был забанен.",reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(f"Пользователь {message.text} уже забанен!!!",reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для дальнейшей работы, нажмите /admin или /start")
    await state.clear()
    del result,useridindb,iduser
@admin_router.message(F.text.lower()=="разбанить")
async def Unban(message:types.Message,state:FSMContext):
    await state.set_state(unbanstate.startunban)
    await message.answer("Выберите пользователя для разбана", reply_markup=keyboardBuilder(False))
@admin_router.message(unbanstate.startunban,F.text != '/cancel')
async def NextUnban(message:types.Message,state:FSMContext):
    useridindb = list(blacklist.find({'username': message.text}))
    iduser = useridindb[0]["id"]
    result = blacklist.find_one({"id":iduser})
    if result is not None:
        blacklist.delete_one({"id":iduser})
    await message.answer(f"Пользователь {message.text} был разбанен.",reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для дальнейшей работы, нажмите /admin или /start")
    await state.clear()
    del result,useridindb,iduser

@admin_router.message(adminstate.startadmin,Command("cancel"))
@admin_router.message(adminstate.useridadmin,Command("cancel"))
@admin_router.message(banstate.startban,Command("cancel"))
@admin_router.message(banstate.endban,Command("cancel"))
@admin_router.message(unbanstate.startunban,Command("cancel"))
async def PhotoCancel(message: types.Message, state:FSMContext):
    await message.answer("Действие отменено, начните сначала",reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text="Выберите действие",reply_markup=callKb())
    await state.clear()
