from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import logging

from utils import db
from utils.helpers import (
    is_dating_message, mute_user, ban_user_chat,
    mention_html, get_chat_admins
)
from utils.texts import t
from config import SPAM_THRESHOLD, SPAM_WINDOW, WARN_LIMIT, MUTE_DURATION

router = Router()
logger = logging.getLogger(__name__)

# Spam tracker: {chat_id: {user_id: [timestamps]}}
message_tracker = defaultdict(lambda: defaultdict(list))

@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member(event: ChatMemberUpdated):
    """Welcome new members"""
    user = event.new_chat_member.user
    if user.is_bot:
        return
    
    # Save group id
    db.set_group_id(event.chat.id)
    db.register_user(user.id, user.username, user.full_name)
    db.increment_stat("total_users")
    
    lang = db.get_bot_lang()
    mention = mention_html(user.id, user.first_name)
    
    welcome_text = (
        f"🎉 {t('welcome_group', lang, name=mention)}\n\n"
        f"📚 <b>Guruh Qoidalari:</b>\n"
        f"1️⃣ Faqat ingliz tili haqida yozing\n"
        f"2️⃣ Spam qilmang\n"
        f"3️⃣ Tanishish uchun bu guruhdan foydalanmang\n"
        f"4️⃣ Bir-biringizga hurmat bilan muomalada bo'ling\n\n"
        f"🤖 Botdan foydalanish uchun: @kibrliybolabot"
    )
    
    try:
        await event.bot.send_message(event.chat.id, welcome_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Welcome message error: {e}")

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_handler(message: Message):
    """Handle all group messages - spam check, dating filter"""
    if not message.from_user or message.from_user.is_bot:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = message.from_user
    lang = db.get_bot_lang()
    
    # Save group
    db.set_group_id(chat_id)
    db.increment_stat("total_messages")
    
    # Check if admin
    try:
        member = await message.bot.get_chat_member(chat_id, user_id)
        is_admin = member.status in ["creator", "administrator"]
    except:
        is_admin = False
    
    if is_admin:
        return  # Don't restrict admins
    
    text = message.text or message.caption or ""
    
    # 1. Dating/tanishish filter
    if is_dating_message(text):
        try:
            await message.delete()
        except:
            pass
        mention = mention_html(user_id, user.first_name)
        warn_count = db.add_warn(user_id, chat_id)
        
        warning_msg = await message.answer(
            t("tanishish_warning", lang, user=mention) +
            f"\n⚠️ Ogohlantirish: <b>{warn_count}/{WARN_LIMIT}</b>",
            parse_mode="HTML"
        )
        
        # Auto-delete warning after 30 seconds
        asyncio.create_task(delete_message_later(message.bot, chat_id, warning_msg.message_id, 30))
        
        if warn_count >= WARN_LIMIT:
            await handle_ban(message, user_id, user.first_name, chat_id, lang)
        return
    
    # 2. Spam check
    now = datetime.now()
    tracker = message_tracker[chat_id][user_id]
    
    # Remove old messages
    tracker[:] = [t for t in tracker if (now - t).total_seconds() < SPAM_WINDOW]
    tracker.append(now)
    
    if len(tracker) >= SPAM_THRESHOLD:
        mention = mention_html(user_id, user.first_name)
        warn_count = db.add_warn(user_id, chat_id)
        
        # Mute user
        await mute_user(message.bot, chat_id, user_id, MUTE_DURATION)
        
        spam_msg = await message.answer(
            t("spam_warning", lang, user=mention) +
            f"\n⚠️ Ogohlantirish: <b>{warn_count}/{WARN_LIMIT}</b>\n"
            f"🔇 10 daqiqa mute qilindi!",
            parse_mode="HTML"
        )
        tracker.clear()
        asyncio.create_task(delete_message_later(message.bot, chat_id, spam_msg.message_id, 30))
        
        if warn_count >= WARN_LIMIT:
            await handle_ban(message, user_id, user.first_name, chat_id, lang)

async def handle_ban(message: Message, user_id: int, name: str, chat_id: int, lang: str):
    """Ban user after 3 warnings"""
    mention = mention_html(user_id, name)
    try:
        await ban_user_chat(message.bot, chat_id, user_id)
        db.ban_user(user_id)
        db.reset_warns(user_id, chat_id)
        await message.answer(t("banned", lang, user=mention), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ban error: {e}")

async def delete_message_later(bot, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass
