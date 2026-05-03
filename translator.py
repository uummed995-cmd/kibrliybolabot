from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.keyboards import back_kb
from utils.texts import t
from utils import db
import logging
import re

router = Router()
logger = logging.getLogger(__name__)

LANG_NAMES = {
    "uz": "O'zbek 🇺🇿",
    "ru": "Русский 🇷🇺",
    "en": "English 🇬🇧",
    "ar": "العربية 🇸🇦",
    "tr": "Türkçe 🇹🇷",
    "fr": "Français 🇫🇷",
    "de": "Deutsch 🇩🇪",
    "ko": "한국어 🇰🇷",
    "zh": "中文 🇨🇳",
    "ja": "日本語 🇯🇵",
    "it": "Italiano 🇮🇹",
    "es": "Español 🇪🇸",
}

class TranslatorState(StatesGroup):
    waiting_text = State()

async def translate_text(text: str, source: str, target: str) -> str:
    """Translate using MyMemory API (free, no key needed)"""
    import aiohttp
    
    lang_pair = f"{source}|{target}"
    url = "https://api.mymemory.translated.net/get"
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {"q": text, "langpair": lang_pair}
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    translated = data.get("responseData", {}).get("translatedText", "")
                    if translated and data.get("responseStatus") == 200:
                        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")
    
    return "❌ Tarjima amalga oshmadi. Keyinroq urinib ko'ring."

@router.callback_query(F.data == "translator")
async def translator_menu(callback: CallbackQuery):
    lang = db.get_bot_lang()
    help_text = t("translator_help", lang)
    help_text += "\n\n✍️ Yozing: <code>uz-en Salom dunyo</code>"
    await callback.message.edit_text(help_text, reply_markup=back_kb(), parse_mode="HTML")
    await callback.answer()

@router.message(F.text.regexp(r'^[a-z]{2}-[a-z]{2}\s+.+'))
async def handle_translation(message: Message):
    """Handle translation request: uz-en Hello world"""
    text = message.text.strip()
    match = re.match(r'^([a-z]{2})-([a-z]{2})\s+(.+)$', text, re.DOTALL)
    
    if not match:
        return
    
    source, target, content = match.group(1), match.group(2), match.group(3)
    
    if source not in LANG_NAMES or target not in LANG_NAMES:
        await message.reply(
            f"❌ Noto'g'ri til kodi!\n\n"
            f"Mavjud tillar: {', '.join(LANG_NAMES.keys())}",
            parse_mode="HTML"
        )
        return
    
    wait_msg = await message.reply("⏳ Tarjima qilinmoqda...")
    
    translated = await translate_text(content, source, target)
    
    result = (
        f"🌐 <b>Tarjima</b>\n\n"
        f"📝 <b>Asl matn</b> ({LANG_NAMES.get(source, source)}):\n"
        f"{content}\n\n"
        f"✅ <b>Tarjima</b> ({LANG_NAMES.get(target, target)}):\n"
        f"{translated}"
    )
    
    await wait_msg.edit_text(result, parse_mode="HTML")
