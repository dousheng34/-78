from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from database import Database


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["db"] = self.db
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user:
            db_user = self.db.get_user(user.id)
            if db_user:
                if self.db.reset_daily_requests_if_needed(db_user):
                    await self.db.save()
            data["db_user"] = db_user
        else:
            data["db_user"] = None

        return await handler(event, data)
