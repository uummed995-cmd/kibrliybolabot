from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime
import asyncio

from utils.keyboards import (
    admin_panel_kb, lang_select_kb, back_kb,
    mandatory_manage_kb, admin_user_manage_kb
)
from utils.texts import t
from utils import db
from utils.helpers import (
    mute_user, ban_user_chat, unban_user_chat, kick_user,
    get_user_info, get_chat_admins, mention_html
)
from config import ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)

class AdminState(StatesGroup):
    broadcast = State()
    add_channel = State()
    waiting_user_id = State()
    waiting_warn_id = State()
    edit_text_key = State()
    edit_text_value = State()
    group_user_id = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ─── Admin Panel Main ───────────────────────────────────────────────────
@router.callback_query(F.data == "admin_panel")
async def admin_panel_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    lang = db.get_bot_lang()
    await callback.message.edit_text(t("admin_panel", lang), reply_markup=admin_panel_kb(), parse_mode="HTML")
    await callback.answer()

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return
    lang = db.get_bot_lang()
    await message.answer(t("admin_panel", lang), reply_markup=admin_panel_kb(), parse_mode="HTML")

# ─── Language ────────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_lang")
async def admin_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    await callback.message.edit_text("🌍 Bot tilini tanlang:", reply_markup=lang_select_kb(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("set_lang_"))
async def set_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    lang = callback.data.replace("set_lang_", "")
    db.set_bot_lang(lang)
    await callback.message.edit_text(t("lang_changed", lang), reply_markup=admin_panel_kb(), parse_mode="HTML")
    await callback.answer("✅")

# ─── Statistics ──────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    lang = db.get_bot_lang()
    stats = db.get_stats()
    users = db.get_all_users()
    tickets = db.get_tickets()
    open_tickets = sum(1 for t in tickets.values() if t.get("status") == "open")
    
    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{len(users)}</b>\n"
        f"💬 Jami xabarlar: <b>{stats.get('total_messages', 0)}</b>\n"
        f"🎮 O'yinlar o'ynalgan: <b>{stats.get('total_games', 0)}</b>\n"
        f"🎫 Ochiq ticketlar: <b>{open_tickets}</b>\n\n"
        f"🤖 Bot: @kibrliybolabot\n"
        f"🕐 Vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb("admin_panel"), parse_mode="HTML")
    await callback.answer()

# ─── Broadcast ───────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    lang = db.get_bot_lang()
    await state.set_state(AdminState.broadcast)
    await callback.message.edit_text(t("broadcast_prompt", lang), reply_markup=back_kb("admin_panel"), parse_mode="HTML")
    await callback.answer()

@router.message(AdminState.broadcast, F.from_user.id == ADMIN_ID)
async def send_broadcast(message: Message, state: FSMContext):
    await state.clear()
    lang = db.get_bot_lang()
    users = db.get_all_users()
    
    count = 0
    for user_id_str in users:
        try:
            await message.bot.copy_message(int(user_id_str), message.chat.id, message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await message.reply(t("broadcast_done", lang, count=count), parse_mode="HTML")

# ─── Mandatory Channels ──────────────────────────────────────────────────
@router.callback_query(F.data == "admin_mandatory")
async def admin_mandatory(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    channels = db.get_mandatory_channels()
    
    if not channels:
        text = "📢 <b>Majburiy A'zolik</b>\n\nHozirda hech qanday kanal/guruh qo'shilmagan."
    else:
        text = "📢 <b>Majburiy A'zolik</b>\n\nQuyidagi kanal/guruhlar ro'yxatda:\n" + "\n".join(f"• {ch}" for ch in channels)
    
    await callback.message.edit_text(text, reply_markup=mandatory_manage_kb(channels), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "add_mandatory_channel")
async def add_mandatory_channel_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    await state.set_state(AdminState.add_channel)
    await callback.message.edit_text(
        "📢 Kanal/Guruh username yoki ID'sini yozing:\n"
        "Misol: <code>@mykanalim</code> yoki <code>-100123456789</code>",
        reply_markup=back_kb("admin_mandatory"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminState.add_channel, F.from_user.id == ADMIN_ID)
async def add_channel_input(message: Message, state: FSMContext):
    await state.clear()
    channel = message.text.strip()
    channels = db.get_mandatory_channels()
    
    # Verify bot is admin in channel
    try:
        chat = await message.bot.get_chat(channel)
        bot_member = await message.bot.get_chat_member(chat.id, (await message.bot.get_me()).id)
        if bot_member.status not in ["administrator", "creator"]:
            await message.reply(
                f"⚠️ Bot {channel} da admin emas!\n"
                f"Iltimos avval botni admin qiling, keyin qayta urinib ko'ring.",
                reply_markup=back_kb("admin_mandatory"),
                parse_mode="HTML"
            )
            return
        
        if channel not in channels:
            channels.append(channel)
            db.set_mandatory_channels(channels)
            await message.reply(f"✅ {channel} qo'shildi!", reply_markup=back_kb("admin_mandatory"))
        else:
            await message.reply("⚠️ Bu kanal/guruh allaqachon ro'yxatda!")
    except Exception as e:
        await message.reply(f"❌ Xato: Kanal topilmadi yoki bot admin emas.\n{e}")

@router.callback_query(F.data.startswith("remove_channel_"))
async def remove_channel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    channel_name = "@" + callback.data.replace("remove_channel_", "")
    channels = db.get_mandatory_channels()
    if channel_name in channels:
        channels.remove(channel_name)
        db.set_mandatory_channels(channels)
    await callback.answer(f"✅ {channel_name} o'chirildi!")
    await admin_mandatory(callback)

@router.callback_query(F.data == "check_mandatory")
async def check_mandatory_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    channels = db.get_mandatory_channels()
    
    results = []
    for ch in channels:
        try:
            bot_me = await callback.bot.get_me()
            member = await callback.bot.get_chat_member(ch, bot_me.id)
            status = "✅ Admin" if member.status in ["administrator", "creator"] else "❌ Admin emas"
        except:
            status = "❌ Kirish yo'q"
        results.append(f"{ch}: {status}")
    
    text = "🔄 <b>Kanal Holati:</b>\n\n" + "\n".join(results) if results else "📋 Kanallar yo'q"
    await callback.answer(text[:200], show_alert=True)

# ─── Users Management ────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    users = db.get_all_users()
    text = f"👥 <b>Foydalanuvchilar</b>\n\nJami: <b>{len(users)}</b> ta\n\nFoydalanuvchini boshqarish uchun ID'sini yozing:"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 ID bilan Qidirish", callback_data="admin_search_user")],
        [InlineKeyboardButton(text="📋 Ro'yxat (Top 10)", callback_data="admin_user_list")],
        [InlineKeyboardButton(text="◀️ Admin Panel", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_search_user")
async def admin_search_user_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    await state.set_state(AdminState.waiting_user_id)
    await callback.message.edit_text(
        "🔍 Foydalanuvchi <b>ID</b> yoki <b>username</b> yozing:",
        reply_markup=back_kb("admin_users"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminState.waiting_user_id, F.from_user.id == ADMIN_ID)
async def search_user(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip().replace("@", "")
    
    try:
        if query.isdigit():
            user_id = int(query)
        else:
            chat = await message.bot.get_chat(f"@{query}")
            user_id = chat.id
        
        info = await get_user_info(message.bot, user_id)
        group_id = db.get_group_id()
        if info:
            score = db.get_user_score(user_id)
            warns = db.get_warns(user_id, group_id or 0)
            user_data = db.get_user(user_id)
            
            text = (
                f"👤 <b>Foydalanuvchi Ma'lumoti</b>\n\n"
                f"🆔 ID: <code>{info['id']}</code>\n"
                f"👤 Ism: {info['full_name']}\n"
                f"📱 Username: @{info['username']}\n"
                f"💰 Ball: {score}\n"
                f"⚠️ Ogohlantirishlar: {warns}/3\n"
                f"📅 Ro'yxatdan: {user_data.get('joined', 'Noma\'lum')[:10] if user_data else 'Noma\'lum'}"
            )
            await message.reply(text, reply_markup=admin_user_manage_kb(user_id, group_id or ""), parse_mode="HTML")
        else:
            await message.reply(t("user_not_found", db.get_bot_lang()), parse_mode="HTML")
    except Exception as e:
        await message.reply(f"❌ Topilmadi: {e}")

@router.callback_query(F.data == "admin_user_list")
async def admin_user_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    users = db.get_all_users()
    
    scores = [(uid, u.get("full_name", "?"), db.get_user_score(int(uid))) 
              for uid, u in users.items()]
    scores.sort(key=lambda x: x[2], reverse=True)
    top = scores[:10]
    
    text = "🏆 <b>Top 10 Foydalanuvchilar</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, name, score) in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {name} — {score} ball\n"
    
    await callback.message.edit_text(text, reply_markup=back_kb("admin_users"), parse_mode="HTML")
    await callback.answer()

# ─── User Actions (Warn/Mute/Ban) ────────────────────────────────────────
@router.callback_query(F.data.startswith("admin_warn_"))
async def admin_warn_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    chat_id = int(parts[3]) if parts[3] and parts[3] != "" and parts[3].lstrip('-').isdigit() else None
    
    if chat_id:
        warn_count = db.add_warn(user_id, chat_id)
        info = await get_user_info(callback.bot, user_id)
        name = info["full_name"] if info else str(user_id)
        mention = mention_html(user_id, name)
        
        try:
            await callback.bot.send_message(
                chat_id,
                f"⚠️ Admin tomonidan ogohlantirish!\n{mention}\nOgohlantirishlar: {warn_count}/3",
                parse_mode="HTML"
            )
        except:
            pass
        
        await callback.answer(f"⚠️ Ogohlantirish #{warn_count} yuborildi!")
    else:
        await callback.answer("❌ Guruh ID topilmadi!")

@router.callback_query(F.data.startswith("admin_mute_"))
async def admin_mute_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    chat_id_str = parts[3] if len(parts) > 3 else ""
    chat_id = int(chat_id_str) if chat_id_str and chat_id_str.lstrip('-').isdigit() else None
    
    if chat_id:
        success = await mute_user(callback.bot, chat_id, user_id, 10)
        await callback.answer("✅ Mute qilindi!" if success else "❌ Xato!")
    else:
        await callback.answer("❌ Guruh ID yo'q!")

@router.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    chat_id_str = parts[3] if len(parts) > 3 else ""
    chat_id = int(chat_id_str) if chat_id_str and chat_id_str.lstrip('-').isdigit() else None
    
    if chat_id:
        success = await ban_user_chat(callback.bot, chat_id, user_id)
        if success:
            db.ban_user(user_id)
        await callback.answer("✅ Ban qilindi!" if success else "❌ Xato!")
    else:
        db.ban_user(user_id)
        await callback.answer("✅ Botdan ban qilindi!")

@router.callback_query(F.data.startswith("admin_unban_"))
async def admin_unban_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    chat_id_str = parts[3] if len(parts) > 3 else ""
    chat_id = int(chat_id_str) if chat_id_str and chat_id_str.lstrip('-').isdigit() else None
    
    db.unban_user(user_id)
    if chat_id:
        await unban_user_chat(callback.bot, chat_id, user_id)
    await callback.answer("✅ Unban qilindi!")

@router.callback_query(F.data.startswith("admin_kick_"))
async def admin_kick_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    chat_id_str = parts[3] if len(parts) > 3 else ""
    chat_id = int(chat_id_str) if chat_id_str and chat_id_str.lstrip('-').isdigit() else None
    
    if chat_id:
        success = await kick_user(callback.bot, chat_id, user_id)
        await callback.answer("✅ Kick qilindi!" if success else "❌ Xato!")
    else:
        await callback.answer("❌ Guruh ID yo'q!")

@router.callback_query(F.data.startswith("admin_info_"))
async def admin_user_info(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    user_id = int(callback.data.split("_")[2])
    info = await get_user_info(callback.bot, user_id)
    
    if info:
        score = db.get_user_score(user_id)
        group_id = db.get_group_id()
        warns = db.get_warns(user_id, group_id or 0)
        user_data = db.get_user(user_id)
        
        text = (
            f"ℹ️ <b>Ma'lumot</b>\n\n"
            f"ID: <code>{info['id']}</code>\n"
            f"Ism: {info['full_name']}\n"
            f"Username: @{info['username']}\n"
            f"Ball: {score}\n"
            f"Ogohlantirishlar: {warns}/3\n"
            f"Ro'yxat: {user_data.get('joined', '?')[:10] if user_data else '?'}"
        )
        await callback.answer(text[:200], show_alert=True)
    else:
        await callback.answer("❌ Ma'lumot topilmadi!")

# ─── Tickets ─────────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_tickets")
async def admin_tickets_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    tickets = db.get_tickets()
    open_tickets = {tid: t for tid, t in tickets.items() if t.get("status") == "open"}
    
    if not open_tickets:
        await callback.message.edit_text(
            "📩 <b>Ticketlar</b>\n\nHozirda ochiq ticketlar yo'q! ✅",
            reply_markup=back_kb("admin_panel"),
            parse_mode="HTML"
        )
    else:
        text = f"📩 <b>Ochiq Ticketlar</b> ({len(open_tickets)} ta)\n\n"
        for tid, ticket in list(open_tickets.items())[:10]:
            text += f"🎫 #{tid} | @{ticket.get('username', '?')} | {ticket.get('time', '?')[:10]}\n"
        
        await callback.message.edit_text(text, reply_markup=back_kb("admin_panel"), parse_mode="HTML")
    await callback.answer()

# ─── Group Settings ───────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_group")
async def admin_group_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    group_id = db.get_group_id()
    
    text = (
        f"🏘 <b>Guruh Sozlamalari</b>\n\n"
        f"📍 Guruh ID: <code>{group_id or 'Belgilanmagan'}</code>\n\n"
        f"Guruhni o'zgartirish uchun botni guruhga qo'shing va /setgroup komandasini yozing."
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Guruh Ma'lumotini Yangilash", callback_data="admin_refresh_group")],
        [InlineKeyboardButton(text="◀️ Admin Panel", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_refresh_group")
async def refresh_group(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    group_id = db.get_group_id()
    if group_id:
        try:
            chat = await callback.bot.get_chat(group_id)
            await callback.answer(f"✅ Guruh: {chat.title}", show_alert=True)
        except:
            await callback.answer("❌ Guruhga kirish mumkin emas!")
    else:
        await callback.answer("❌ Guruh belgilanmagan!")

@router.message(Command("setgroup"))
async def set_group_cmd(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        if is_admin(message.from_user.id):
            db.set_group_id(message.chat.id)
            await message.reply(f"✅ Guruh saqlandi!\nID: <code>{message.chat.id}</code>", parse_mode="HTML")

# ─── Bot Info ─────────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_bot_info")
async def admin_bot_info(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    bot_me = await callback.bot.get_me()
    users = db.get_all_users()
    lang = db.get_bot_lang()
    
    text = (
        f"🤖 <b>Bot Ma'lumoti</b>\n\n"
        f"📛 Nomi: {bot_me.full_name}\n"
        f"🆔 ID: <code>{bot_me.id}</code>\n"
        f"📱 Username: @{bot_me.username}\n"
        f"🌍 Til: {lang}\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"📋 Majburiy kanallar: {len(db.get_mandatory_channels())}\n"
        f"🕐 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb("admin_panel"), parse_mode="HTML")
    await callback.answer()

# ─── Manage Group Users ───────────────────────────────────────────────────
@router.callback_query(F.data == "admin_manage_user")
async def admin_manage_group_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    group_id = db.get_group_id()
    
    if not group_id:
        await callback.answer("❌ Guruh belgilanmagan! /setgroup komandasini ishlating.", show_alert=True)
        return
    
    await state.set_state(AdminState.group_user_id)
    await callback.message.edit_text(
        f"👤 <b>Guruh Foydalanuvchisini Boshqarish</b>\n\n"
        f"Guruh: <code>{group_id}</code>\n\n"
        f"Foydalanuvchi <b>ID</b> yoki <b>@username</b> yozing:",
        reply_markup=back_kb("admin_panel"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminState.group_user_id, F.from_user.id == ADMIN_ID)
async def handle_group_user_id(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
    group_id = db.get_group_id()
    
    try:
        if query.lstrip('-').isdigit():
            user_id = int(query)
        else:
            user = await message.bot.get_chat(query.lstrip('@'))
            user_id = user.id
        
        info = await get_user_info(message.bot, user_id, group_id)
        if info:
            score = db.get_user_score(user_id)
            warns = db.get_warns(user_id, group_id)
            
            text = (
                f"👤 <b>Guruh A'zosi</b>\n\n"
                f"🆔 ID: <code>{info['id']}</code>\n"
                f"👤 Ism: {info['full_name']}\n"
                f"📱 Username: @{info['username']}\n"
                f"💰 Ball: {score}\n"
                f"⚠️ Ogohlantirishlar: {warns}/3\n"
                f"📊 Holat: {info.get('status', '?')}"
            )
            await message.reply(
                text,
                reply_markup=admin_user_manage_kb(user_id, group_id),
                parse_mode="HTML"
            )
        else:
            await message.reply("❌ Foydalanuvchi topilmadi!")
    except Exception as e:
        await message.reply(f"❌ Xato: {e}")

# ─── Edit Texts ───────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin_edit_texts")
async def admin_edit_texts(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    await callback.message.edit_text(
        "✏️ <b>Matnlarni Tahrirlash</b>\n\n"
        "Bu funksiya tez orada qo'shiladi.\n"
        "Hozircha <code>utils/texts.py</code> faylini tahrirlang.",
        reply_markup=back_kb("admin_panel"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("❌ Bekor qilindi!")
    await admin_panel_cb(callback)
