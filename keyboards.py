from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.texts import t

def main_menu_kb(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 O'yinlar", callback_data="games"),
            InlineKeyboardButton(text="🌐 Tarjimon", callback_data="translator"),
        ],
        [
            InlineKeyboardButton(text="🎁 Kunlik Bonus", callback_data="bonus"),
            InlineKeyboardButton(text="😄 Qiziqarli", callback_data="fun"),
        ],
        [
            InlineKeyboardButton(text="📩 Adminga Xabar", callback_data="contact_admin"),
            InlineKeyboardButton(text="💰 Ballarim", callback_data="my_score"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help"),
        ]
    ])

def games_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🧠 Trivia Quiz", callback_data="game_trivia"),
            InlineKeyboardButton(text="🔢 Matematik Duel", callback_data="game_math"),
        ],
        [
            InlineKeyboardButton(text="📝 So'z O'yini", callback_data="game_word"),
            InlineKeyboardButton(text="🍀 Omad Toshi", callback_data="game_luck"),
        ],
        [
            InlineKeyboardButton(text="🎭 Topishmoq", callback_data="game_riddle"),
            InlineKeyboardButton(text="🎯 Bilimdon", callback_data="game_knowledge"),
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_menu"),
        ]
    ])

def fun_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😂 Latifa", callback_data="fun_joke"),
            InlineKeyboardButton(text="🤯 Qiziq Fakt", callback_data="fun_fact"),
        ],
        [
            InlineKeyboardButton(text="💡 Iqtibos", callback_data="fun_quote"),
            InlineKeyboardButton(text="⭐ Horoscope", callback_data="fun_horoscope"),
        ],
        [
            InlineKeyboardButton(text="☀️ Kun Maslahati", callback_data="fun_tip"),
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_menu"),
        ]
    ])

def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌍 Bot Tili", callback_data="admin_lang"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Majburiy A'zolik", callback_data="admin_mandatory"),
            InlineKeyboardButton(text="📣 Broadcast", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📩 Ticketlar", callback_data="admin_tickets"),
        ],
        [
            InlineKeyboardButton(text="🏘 Guruh Sozlamalari", callback_data="admin_group"),
            InlineKeyboardButton(text="🔧 Guruh Boshqaruv", callback_data="admin_manage_user"),
        ],
        [
            InlineKeyboardButton(text="✏️ Matnlarni Tahrirlash", callback_data="admin_edit_texts"),
            InlineKeyboardButton(text="🤖 Bot Ma'lumoti", callback_data="admin_bot_info"),
        ],
        [
            InlineKeyboardButton(text="◀️ Asosiy Menyu", callback_data="main_menu"),
        ]
    ])

def lang_select_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="set_lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")]
    ])

def back_kb(callback="main_menu"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data=callback)]
    ])

def confirm_kb(action, item_id=""):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_action"),
        ]
    ])

def ticket_reply_kb(ticket_id, user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob Berish", callback_data=f"reply_ticket_{ticket_id}_{user_id}")],
        [InlineKeyboardButton(text="✅ Yopish", callback_data=f"close_ticket_{ticket_id}")],
    ])

def admin_user_manage_kb(user_id, chat_id=""):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚠️ Warn", callback_data=f"admin_warn_{user_id}_{chat_id}"),
            InlineKeyboardButton(text="🔇 Mute", callback_data=f"admin_mute_{user_id}_{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="🚫 Ban", callback_data=f"admin_ban_{user_id}_{chat_id}"),
            InlineKeyboardButton(text="✅ Unban", callback_data=f"admin_unban_{user_id}_{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="👢 Kick", callback_data=f"admin_kick_{user_id}_{chat_id}"),
            InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data=f"admin_info_{user_id}"),
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_users")]
    ])

def mandatory_manage_kb(channels):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"❌ {ch}", callback_data=f"remove_channel_{ch.replace('@','')}")])
    buttons.append([InlineKeyboardButton(text="➕ Kanal/Guruh Qo'shish", callback_data="add_mandatory_channel")])
    buttons.append([
        InlineKeyboardButton(text="🔄 Holatini Tekshirish", callback_data="check_mandatory"),
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def trivia_answer_kb(options, correct_idx, question_id):
    buttons = []
    for i, opt in enumerate(options):
        buttons.append([InlineKeyboardButton(
            text=f"{['A', 'B', 'C', 'D'][i]}) {opt}",
            callback_data=f"trivia_{question_id}_{i}_{correct_idx}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def join_channels_kb(channels):
    buttons = []
    for ch in channels:
        name = ch if ch.startswith("http") else f"https://t.me/{ch.strip('@')}"
        buttons.append([InlineKeyboardButton(text=f"➡️ {ch}", url=name)])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_joined")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
