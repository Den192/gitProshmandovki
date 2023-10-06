from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from pymongo import MongoClient
mongo = MongoClient()
db = mongo.ProshmandovkiTgBot
blacklist = db.blacklist

# Это будет outer-мидлварь на любые колбэки
class BlacklistMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        userid = event.from_user.id 
        cursor = blacklist.find({},{"_id":0,'id': 1})
        list_cursor = [result for result in cursor]
        editedcursor = [result["id"] for result in list_cursor]
        if userid in editedcursor:
            await event.answer("Вы были забанены!!!", show_alert=True)
            return
        else:
            return await handler(event,data)
