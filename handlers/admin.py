import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database
from keyboards.admin_kb import get_admin_menu
from keyboards.main_kb import get_back_button
from config import ADMIN_ID

router = Router()
logger = logging.getLogger(__name__)


class BroadcastState(StatesGroup):
    waiting = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Database):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён")
        return
    stats = db.get_stats()
    text = f"""🔧 <b>Панель администратора</b>

📊 Пользователей: {stats.get('total_users', 0)}
💰 Транзакций: {stats.get('total_transactions', 0)}
⭐ Заработано Stars: {stats.get('total_revenue_stars', 0)}"""
    await message.answer(text, reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_stats")
async def on_stats(callback: CallbackQuery, db: Database):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    stats = db.get_stats()
    users = db.get_all_users()
    free = sum(1 for u in users.values() if u.get("subscription") == "free")
    pro  = sum(1 for u in users.values() if u.get("subscription") == "pro")
    vip  = sum(1 for u in users.values() if u.get("subscription") == "vip")
    total = stats.get('total_users', 0)
    stars = stats.get('total_revenue_stars', 0)
    conv = f"{((pro + vip) / max(1, total) * 100):.1f}%"
    text = f"""📊 <b>Статистика</b>

👥 Всего: {total}
🆓 Free: {free} | 💎 Pro: {pro} | 👑 VIP: {vip}

💰 Транзакций: {stats.get('total_transactions', 0)}
⭐ Stars: {stars} (~${stars * 0.013:.2f})
📈 Конверсия: {conv}"""
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def on_users(callback: CallbackQuery, db: Database):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    users = list(db.get_all_users().values())[-10:]
    text = "👥 <b>Последние 10 пользователей:</b>\n\n"
    for u in users:
        text += f"• {u.get('first_name','?')} (@{u.get('username','?')}) — {u.get('subscription','free')}\n"
    await callback.message.edit_text(text or "Нет пользователей", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_transactions")
async def on_transactions(callback: CallbackQuery, db: Database):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    txs = db.get_transactions(10)
    text = "💰 <b>Транзакции:</b>\n\n"
    if not txs:
        text += "Пока нет транзакций"
    else:
        for t in reversed(txs):
            text += f"• {t['timestamp'][:10]} {t['amount']}⭐ {t['service']} (ID:{t['user_id']})\n"
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def on_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    await state.set_state(BroadcastState.waiting)
    await callback.message.edit_text(
        "📢 <b>Рассылка</b>\n\nНапишите сообщение для всех пользователей:",
        reply_markup=get_back_button("main_menu")
    )
    await callback.answer()


@router.message(BroadcastState.waiting)
async def on_broadcast_msg(message: Message, state: FSMContext, db: Database):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    users = db.get_all_users()
    sent, failed = 0, 0
    status = await message.answer(f"📢 Начинаю рассылку... 0/{len(users)}")
    for uid in users:
        try:
            await message.bot.send_message(int(uid), f"📢 <b>Сообщение от администратора:</b>\n\n{message.text}")
            sent += 1
        except Exception:
            failed += 1
    await status.edit_text(f"✅ Рассылка завершена!\nОтправлено: {sent} | Ошибок: {failed}")
    await state.clear()
