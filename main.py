from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
import os

TOKEN = os.getenv("BOT_TOKEN")  # חשוב לוודא שהוספת את זה ב-secrets בריילווי בשם BOT_TOKEN

# הפקודה /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Repeat this sentence:\nShe sells seashells by the seashore.\n\nNow send me your voice saying the same sentence!")

# קבלת הודעות קוליות
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.voice.file_id)
    await file.download_to_drive("voice.ogg")

    recognizer = sr.Recognizer()
    with sr.AudioFile("voice.ogg") as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        if text.lower().strip() == "she sells seashells by the seashore":
            await update.message.reply_text("✅ Great job! You said it correctly.")
        else:
            await update.message.reply_text(f"❌ You said: \"{text}\"\nTry again!")
    except Exception as e:
        await update.message.reply_text("Sorry, I couldn't understand you.")

# הרצת הבוט
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()
