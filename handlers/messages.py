from typing import Any
from aiogram import Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto
from pymongo import MongoClient
from aiogram import Router


router=Router()

bot = Bot(token="6390983781:AAF5Jxq5RQJbePhGPg19jxF1r9oxbHP2Nm0")
storage = MemoryStorage()
mongo = MongoClient()
db = mongo.ProshmandovkiTgBot
user_id_collection=db.users
message_history=db.message_history
report_history=db.report_history

class reportstate(StatesGroup):
    startreport=State()
    endreport=State()


class getstate(StatesGroup):
    addcandidate = State()
    photocandidate = State()
    drcandidate = State()
    textcandidate = State()

chatId="-4056699312"




kb=[
        [
            types.KeyboardButton(text="Добавить кандидата"),
            types.KeyboardButton(text="Отправить репорт")
        ],
    ]
keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
kbphoto=[
        [
            types.KeyboardButton(text="Завершить добавление")
        ],
    ]
keyboardphoto = types.ReplyKeyboardMarkup(
        keyboard=kbphoto,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )



@router.message(Command("report"))
@router.message(F.text.lower()=="отправить репорт")
async def reportMessage(message: types.Message,state:FSMContext):
    await state.set_state(reportstate.startreport)
    await message.answer("Напишите дату поста",reply_markup=types.ReplyKeyboardRemove())
"""
@router.message(F.text.lower()=="отправить репорт")
async def reportMessage(message: types.Message,state:FSMContext):
    await state.set_state(reportstate.startreport)
    await message.answer("Напишите дату поста и причину репорта",reply_markup=types.ReplyKeyboardRemove())
"""
@router.message(reportstate.startreport,F.text!="/cancel")
async def dateReport(message:types.Message,state:FSMContext):
    await state.set_state(reportstate.endreport)
    await state.update_data(ReportDate=message.text)
    await message.answer("Напишите причину репорта")
@router.message(reportstate.endreport, F.text!="/cancel")
async def reportMessage(message: types.Message, state:FSMContext):
    data = await state.get_data()
    report_history.insert_one({"UserID":message.from_user.id,"UserNickname":message.chat.username,"ReportDate":data['ReportDate'], "ReportMessage":message.text})
    await bot.send_message(chatId, text="Пришел репорт от пользователя:@"+message.chat.username+"\nДата поста: "+data['ReportDate']+"\nТекст обращения: "+message.text)
    await message.answer("Жалоба приянта! Администраторы уже изучают ваш репорт", reply_markup=keyboard)
    await state.clear()





@router.message(Command("addcandidate"))
@router.message(F.text.lower() == "добавить кандидата")
async def candidate_polling(message: types.Message, state:FSMContext):
    await message.answer("Отправьте фото/видео/gif вашего кандидата в прошмандовки\nЕсли отправляете фото, то должно быть только одно фото в сообщении", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(getstate.addcandidate)
    await state.update_data(photolist=list())
@router.message(getstate.addcandidate, F.photo)
async def candidate_addphoto(message: types.Message, state:FSMContext):
    photolist=list()
    data = await state.get_data()
    data['photolist'].append(message.photo[-1].file_id)
    await state.update_data(photolist,contenttype="groupphoto")
    await message.answer("Фото добавлено, можно отправить еще фотографию. Для завершения, нажмите кнопку",reply_markup=keyboardphoto)
@router.message(getstate.addcandidate,F.text.lower()=="завершить добавление")
async def endphoto_candidate(message: types.Message,state:FSMContext):
    await state.set_state(getstate.drcandidate)
    await message.answer("Введите день рождения/знак зодиака прошмандовки",reply_markup=types.ReplyKeyboardRemove())

@router.message(getstate.addcandidate, F.animation)
async def getvideoandreply(message: types.Message,state:FSMContext):
    await state.set_state(getstate.drcandidate)
    await state.update_data(photo=message.animation.file_id,contenttype="animation")
    await message.answer("Добавьте день рождения/знак зодиака прошмандовки")
@router.message(getstate.addcandidate, F.video)
async def getgifandreply(message: types.Message,state:FSMContext):
    await state.set_state(getstate.drcandidate)
    await state.update_data(photo=message.video.file_id,contenttype="video")
    await message.answer("Добавьте день рождения/знак зодиака прошмандовки")

"""@router.message(getstate.addcandidate,F.text!="/cancel",F.photo)
async def drCandidate(message:types.Message,state:FSMContext):
    await state.set_state(getstate.drcandidate)
    await state.update_data(photo=message.photo[-1].file_id,contenttype="photo")
    #await bot.send_photo(chatId, message.photo[-1].file_id,caption="От пользователя @"+message.chat.username)
    await message.answer("Введите день рождения/знак зодиака прошмандовки")
"""
@router.message(getstate.addcandidate, F.photo==None, F.video==None, F.animation==None, F.text!="/cancel")
async def somethingWrong(message: types.Message):
    await message.answer("Что-то пошло не так, повторите последний пункт",reply_markup=keyboardphoto)


@router.message(getstate.drcandidate,F.text!="/cancel")
async def getPictureAndReply(message: types.Message, state:FSMContext):
    await state.set_state(getstate.photocandidate)
    await message.answer("А теперь напишите текст(до 400 символов)")
    await state.update_data(datebirth=message.text)

@router.message(getstate.photocandidate, F.photo==any, F.text!="/cancel")
@router.message(getstate.drcandidate, F.sticker)
@router.message(getstate.drcandidate, F.photo)
@router.message(getstate.drcandidate, F.video)
@router.message(getstate.drcandidate, F.animation)
@router.message(getstate.photocandidate, F.sticker)
@router.message(getstate.photocandidate, F.video)
@router.message(getstate.photocandidate, F.photo)
@router.message(getstate.photocandidate, F.animation)
async def somethingWrongPhoto(message: types.Message):
    await message.answer("Что-то пошло не так, повторите последний пункт")    

@router.message(F.text!="/cancel", getstate.photocandidate)
async def getText(message: types.Message, state:FSMContext):
    user_data = await state.get_data()
    if message.text is not None and len(message.text)<=400:
        match user_data["contenttype"]:
            case "photo":
                message_history.insert_one({"UserID": message.from_user.id,"UserNickname":message.chat.username,"PhotoLink":user_data['photo'], "DateBirth":user_data["datebirth"],"MessageText":message.text})
                await bot.send_photo(chatId, user_data['photo'], caption="Сообщение от пользователя @"+message.chat.username+"\n"+"Дата рождения: "+user_data['datebirth']+"\n"+message.text)
            case "video":
                message_history.insert_one({"UserID": message.from_user.id,"UserNickname":message.chat.username,"PhotoLink":user_data['photo'], "DateBirth":user_data["datebirth"],"MessageText":message.text})
                await bot.send_video(chatId, user_data['photo'], caption="Сообщение от пользователя @"+message.chat.username+"\n"+"Дата рождения: "+user_data['datebirth']+"\n"+message.text)
            case "animation":
                message_history.insert_one({"UserID": message.from_user.id,"UserNickname":message.chat.username,"PhotoLink":user_data['photo'], "DateBirth":user_data["datebirth"],"MessageText":message.text})
                await bot.send_animation(chatId, user_data['photo'], caption="Сообщение от пользователя @"+message.chat.username+"\n"+"Дата рождения: "+user_data['datebirth']+"\n"+message.text)       
            case "groupphoto":
                i=0
                media_group=list()
                medialink=list()
                while i < len(user_data['photolist']):
                    media=InputMediaPhoto(media=user_data['photolist'][i])
                    media_group.append(media)
                    medialink.append(user_data['photolist'][i])
                    del media
                    i+=1
                message_history.insert_one({"UserID": message.from_user.id,"UserNickname":message.chat.username,"PhotoLink":medialink, "DateBirth":user_data["datebirth"],"MessageText":message.text})
                await bot.send_media_group(chatId, media=media_group)
                await bot.send_message(chatId, text="Сообщение от пользователя @"+message.chat.username+"\n"+"Дата рождения: "+user_data['datebirth']+"\n"+message.text)
                del i,media_group,medialink
        #await bot.send_photo(chatId, user_data['photo'], caption="Сообщение от пользователя @"+message.chat.username+"\n"+"Дата рождения: "+user_data['datebirth']+"\n"+message.text)
    else:
        await message.answer("Количество символов свыше 400, введите сообщение еще раз")
        return
    await message.answer("Cпасибо за информацию! Наши администаторы уже изучают новую прошмандовку!\nМожете отправить новую заявку, нажав на меню или на /addcandidate",reply_markup=keyboard)
    await state.clear()

"""@router.message(getstate.photocandidate, Command("cancel"))
async def PhotoCancel(message: types.Message, state:FSMContext):
    await bot.send_message(chatId, text="Пользователь @"+message.chat.username+" отменил написание текста для фото")
    await message.answer("Действие отменено, начните сначала",reply_markup=keyboard)
    await state.clear()
@router.message(reportstate.startreport, Command("cancel"))
async def ReportCancel(message: types.Message, state:FSMContext):
    await bot.send_message(chatId, text="Пользователь @"+message.chat.username+" отменил написание текста для репорта")
    await message.answer("Действие отменено, начните сначала",reply_markup=keyboard)
    await state.clear()
"""
@router.message(reportstate.startreport,Command("cancel"))
@router.message(reportstate.endreport,Command("cancel"))
@router.message(getstate.addcandidate,Command("cancel"))
@router.message(getstate.drcandidate,Command("cancel"))
@router.message(getstate.photocandidate,Command("cancel"))
async def PhotoCancel(message: types.Message, state:FSMContext):
    await message.answer("Действие отменено, начните сначала",reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text="Выберите действие",reply_markup=keyboard)
    await state.clear()
"""
@router.message(F.text!="Добавить кандидата", F.text!="Отправить репорт")
async def NothingChoosed(message: types.Message):
    await message.answer("Выберите комманду для начала работы",reply_markup=keyboard)
"""