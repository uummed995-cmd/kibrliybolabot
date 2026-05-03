# 🤖 KibrliyBolaBot

Ingliz tili guruhi uchun professional Telegram boti.

## ✨ Imkoniyatlar

### 👥 Guruh Boshqaruvi
- ✅ Spam himoyasi (ko'p xabar = ogohlantirish)
- ✅ Tanishish filtri (yosh, ism so'ragan xabarlarni o'chiradi)
- ✅ 3 ogohlantirish = avtomatik ban
- ✅ 10 daqiqa mute tizimi
- ✅ QuizBot monitoring + admin xabardori
- ✅ Yangi a'zolarni kutib olish

### 🎮 O'yinlar
- 🧠 Trivia Quiz (ingliz tili savollari)
- 🔢 Matematik Duel
- 📝 So'z O'yini (scramble)
- 🍀 Omad Toshi
- 🎭 Topishmoq
- 🎯 Bilimdon

### 🌐 Tarjimon
- 12+ tilda tarjima (uz, ru, en, ar, tr, fr, de, ko, zh, ja, it, es)
- Format: `uz-en Salom dunyo`

### 🎁 Kunlik Bonus
- Har 24 soatda 10-100 ball
- Ball tizimi

### 😄 Qiziqarli Bo'lim
- Latifalar (3 tilda)
- Qiziqarli faktlar
- Ilhomlantiruvchi iqtiboslar
- Horoscope
- Kun maslahati

### 📩 Adminga Xabar (Ticket Tizimi)
- To'liq foydalanuvchi ma'lumoti
- Admin javob berguncha ochiq chat
- Ticket ID tizimi

### ⚙️ Admin Panel
- Bot tilini o'zgartirish (uz/ru/en)
- Majburiy a'zolik (kanal/guruh + avtomatik tekshirish)
- Foydalanuvchilar boshqaruvi (warn/mute/ban/unban/kick)
- Broadcast xabar
- Statistika
- Guruh foydalanuvchisini boshqarish

## 🚀 O'rnatish

### Railway orqali (tavsiya etiladi)

1. GitHub'ga fork qiling
2. [Railway.app](https://railway.app) ga kiring
3. "New Project" → "Deploy from GitHub repo"
4. Environment variables qo'shing:
   ```
   BOT_TOKEN=your_token
   ADMIN_ID=your_id
   ```
5. Deploy!

### Lokal o'rnatish

```bash
git clone https://github.com/sizning_username/kibrliy-bot
cd kibrliy-bot
pip install -r requirements.txt
cp .env.example .env
# .env faylini tahrirlang
python bot.py
```

## 📋 Komandalar

| Komanda | Izoh |
|---------|------|
| `/start` | Botni ishga tushirish |
| `/admin` | Admin panel (faqat admin) |
| `/panel` | Admin panel |
| `/setgroup` | Guruhni belgilash (guruhda) |
| `/help` | Yordam |

## ⚙️ Sozlamalar

Bot Railway'da ishlaydi. `data/bot_data.json` faylida ma'lumotlar saqlanadi.

## 🌍 Tillar

Bot 3 tilda ishlaydi: O'zbek 🇺🇿, Русский 🇷🇺, English 🇬🇧

---
Made with ❤️ for English learning community
