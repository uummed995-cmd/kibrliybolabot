from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import random
from utils.keyboards import back_kb, ticket_reply_kb
from utils.texts import t
from utils import db
from config import ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)

class ContactState(StatesGroup):
    waiting_message = State()
    waiting_reply = State()

active_chats = {}  # {ticket_id: {"user_id": ..., "admin_replying": False}}

@router.callback_query(F.data == "contact_admin")
async def contact_admin_menu(callback: CallbackQuery, state: FSMContext):
    lang = db.get_bot_lang()
    await state.set_state(ContactState.waiting_message)
    
    await callback.message.edit_text(
        t("contact_admin", lang),
        reply_markup=back_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(ContactState.waiting_message)
async def receive_user_message(message: Message, state: FSMContext):
    user = message.from_user
    lang = db.get_bot_lang()
    
    ticket_id = random.randint(10000, 99999)
    time_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Store ticket
    db.create_ticket(ticket_id, user.id, user.username or "yo'q", message.text or "[media]", time_str)
    active_chats[ticket_id] = {"user_id": user.id, "status": "open"}
    
    # Get user's group join date if possible
    group_id = db.get_group_id()
    join_info = "Ma'lumot yo'q"
    if group_id:
        try:
            member = await message.bot.get_chat_member(group_id, user.id)
            join_info = "A'zo"
        except:
            join_info = "Guruhda yo'q"
    
    ticket_text = (
        f"🎫 <b>Ticket #{ticket_id}</b>\n\n"
        f"📩 <b>Yangi Xabar!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {user.full_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📱 <b>Username:</b> @{user.username or 'yo\'q'}\n"
        f"🕐 <b>Vaqt:</b> {time_str}\n"
        f"🏘 <b>Guruh holati:</b> {join_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 <b>Xabar:</b>\n{message.text or '[Rasm/Fayl]'}"
    )
    
    await state.clear()
    
    try:
        await message.bot.send_message(
            ADMIN_ID,
            ticket_text,
            reply_markup=ticket_reply_kb(ticket_id, user.id),
            parse_mode="HTML"
        )
        await message.reply(t("admin_msg_received", lang), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ticket send error: {e}")
        await message.reply("✅ Xabaringiz yetkazildi!", parse_mode="HTML")

@router.callback_query(F.data.startswith("reply_ticket_"))
async def admin_reply_ticket(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    
    parts = callback.data.split("_")
    ticket_id = parts[2]
    user_id = int(parts[3])
    
    await state.set_state(ContactState.waiting_reply)
    await state.update_data(ticket_id=ticket_id, user_id=user_id)
    
    await callback.message.reply(
        f"✍️ Ticket #{ticket_id} uchun javob yozing:\n(Foydalanuvchi ID: <code>{user_id}</code>)",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(ContactState.waiting_reply, F.from_user.id == ADMIN_ID)
async def send_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    ticket_id = data.get("ticket_id")
    
    await state.clear()
    
    try:
        reply_text = (
            f"📩 <b>Admin Javobi</b>\n"
            f"🎫 Ticket #{ticket_id}\n\n"
            f"💬 {message.text}"
        )
        await message.bot.send_message(user_id, reply_text, parse_mode="HTML")
        await message.reply(f"✅ Javob #{ticket_id} ticketga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Xato: {e}")

@router.callback_query(F.data.startswith("close_ticket_"))
async def close_ticket(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    
    ticket_id = callback.data.split("_")[2]
    db.close_ticket(ticket_id)
    
    ticket = db.get_ticket(ticket_id)
    if ticket:
        user_id = ticket.get("user_id")
        try:
            await callback.bot.send_message(
                user_id,
                f"✅ Ticket #{ticket_id} yopildi.\nSavolingiz hal qilindi deb umid qilamiz!",
                parse_mode="HTML"
            )
        except:
            pass
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>YOPILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Ticket yopildi!")
