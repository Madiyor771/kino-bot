from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# === Sizning ma'lumotlaringiz ===
TOKEN = "7688599401:AAGowg5Zb9_RCbiEONxdgS0ijwYTKz-ue0c"
ADMIN_ID = 2002585324  # Sizning ID'ingiz

DB_FILE = "movies.json"

# Bazani yuklash
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Bazani saqlash
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

db = load_db()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Kino kodini yuboring (masalan: DEAD2024)\n\nAdmin bo'lsangiz: /panel"
    )

# Admin panel
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    text = "🔧 Admin paneli\n\nYangi kino qo'shish → /add\n\nMavjud kinolar:\n"
    if not db:
        text += "Hozircha kino yo'q"
    else:
        for code, info in db.items():
            text += f"🎥 {code} → {info['title']}\n"
    await update.message.reply_text(text)

# Kino qo'shish jarayoni
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "Yangi kino qo'shish:\n\n"
        "1️⃣ Avval kino faylini yuboring (video yoki document)\n"
        "2️⃣ Keyin kod yozing (masalan: SPIDER2025)"
    )
    context.user_data["add_mode"] = True

# Xabarlar bilan ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip().upper() if update.message.text else None

    # Admin kino fayl yuborsa
    if user_id == ADMIN_ID and context.user_data.get("add_mode"):
        if update.message.video or update.message.document:
            file = update.message.video or update.message.document
            context.user_data["file_id"] = file.file_id
            context.user_data["title"] = update.message.caption or "Noma'lum kino"
            await update.message.reply_text("✅ Fayl qabul qilindi!\n\nEndi kod yuboring (lotin + raqam):")
            return

    # Admin kod yuborsa
    if user_id == ADMIN_ID and context.user_data.get("add_mode") and text and len(text) >= 4:
        code = text
        if code in db:
            await update.message.reply_text("❌ Bu kod allaqachon bor!")
            return
        db[code] = {
            "file_id": context.user_data["file_id"],
            "title": context.user_data["title"]
        }
        save_db(db)
        await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo'shildi!\nKodi: {code}")
        context.user_data.clear()
        return

    # Oddiy user kod yuborsa
    if text and text in db:
        movie = db[text]
        await update.message.reply_text(f"🎥 {movie['title']}\nYuklanmoqda...")
        await context.bot.send_video(
            chat_id=user_id,
            video=movie["file_id"],
            caption=f"🎬 {movie['title']}\nKodi: {text}\n\n@SizningKanalingiz"
        )
    elif text:
        await update.message.reply_text("❌ Bunday kod topilmadi!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi... 24/7")
    app.run_polling()

if __name__ == "__main__":
    main()
