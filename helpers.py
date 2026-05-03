from aiogram import Bot
from aiogram.types import ChatPermissions
from datetime import datetime, timedelta
import re

DATING_KEYWORDS = [
    "yoshim", "yosh", "born", "age", "birth", "yillik", "yilda tug", "tug'ildim",
    "tanishaylik", "tanishmoq", "tanishamizmi", "salom qizlar", "salom yigitlar",
    "qizlar bormi", "yigitlar bormi", "do'st", "дружить", "познакомим", "сколько лет",
    "how old", "let's be friends", "wanna talk", "dm me", "личка", "lichka",
    "tanishaman", "tanishing", "19 yosh", "20 yosh", "21 yosh", "22 yosh",
    "23 yosh", "24 yosh", "18 yosh", "17 yosh",
]

def is_dating_message(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for keyword in DATING_KEYWORDS:
        if keyword in text_lower:
            return True
    # Check age pattern like "18", "19", "20" alone or with year
    age_pattern = r'\b(1[4-9]|2[0-9])\b.{0,20}(yosh|year|лет|yoshda)'
    if re.search(age_pattern, text_lower):
        return True
    return False

async def mute_user(bot: Bot, chat_id: int, user_id: int, minutes: int = 10):
    until = datetime.now() + timedelta(minutes=minutes)
    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
            ),
            until_date=until
        )
        return True
    except Exception as e:
        return False

async def unmute_user(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        return True
    except:
        return False

async def ban_user_chat(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except:
        return False

async def unban_user_chat(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id, only_if_banned=True)
        return True
    except:
        return False

async def kick_user(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except:
        return False

async def get_chat_admins(bot: Bot, chat_id: int):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        return [a.user.id for a in admins if not a.user.is_bot]
    except:
        return []

async def get_user_info(bot: Bot, user_id: int, chat_id: int = None):
    try:
        user = await bot.get_chat(user_id)
        info = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "yo'q",
            "full_name": user.full_name,
        }
        if chat_id:
            try:
                member = await bot.get_chat_member(chat_id, user_id)
                info["status"] = member.status
            except:
                info["status"] = "unknown"
        return info
    except:
        return None

def mention_html(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'

def format_timedelta(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}s {minutes}d"
    elif minutes > 0:
        return f"{minutes}d {secs}s"
    else:
        return f"{secs}s"

async def check_mandatory_membership(bot: Bot, user_id: int, channels: list) -> list:
    """Returns list of channels user is NOT subscribed to"""
    not_subscribed = []
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked", "banned"]:
                not_subscribed.append(channel)
        except:
            not_subscribed.append(channel)
    return not_subscribed
