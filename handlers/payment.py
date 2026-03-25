import logging
from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery
from database import Database
from services.subscription import get_subscription_end_date

router = Router()
logger = logging.getLogger(__name__)

SERVICE_MAP = {
    "one_resume":   ("resume",   "📄 Опишите опыт, навыки и желаемую должность:"),
    "one_business": ("business", "📋 Опишите вашу бизнес-идею:"),
    "one_content":  ("content",  "✍️ Укажите тему для создания контента:"),
}


@router.pre_checkout_query()
async def on_pre_checkout(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message, db: Database):
    payment = message.successful_payment
    payload = payment.invoice_payload
    stars = payment.total_amount
    user_id = message.from_user.id

    await db.add_transaction(user_id=user_id, amount=stars, service=payload, payload=payload)

    if payload == "sub_pro":
        await db.update_user(user_id, subscription="pro", subscription_end=get_subscription_end_date(1))
        await message.answer("✅ <b>Pro активирован!</b>\n\n💎 Безлимитный доступ на 30 дней!\nНажмите /start")

    elif payload == "sub_vip":
        await db.update_user(user_id, subscription="vip", subscription_end=get_subscription_end_date(1))
        await message.answer("✅ <b>VIP активирован!</b>\n\n👑 Элитный доступ на 30 дней!\nНажмите /start")

    elif payload in SERVICE_MAP:
        service_type, prompt = SERVICE_MAP[payload]
        await db.update_user(user_id, pending_service=service_type)
        await message.answer(f"✅ <b>Оплата прошла!</b>\n\n{prompt}")

    logger.info(f"Payment: user={user_id}, payload={payload}, stars={stars}")
