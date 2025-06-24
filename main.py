import os
import tempfile
import logging
import speech_recognition as sr

from telegram import Update, Voice
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# קונפיגורציית לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")


# פונקציה שממירה הודעת קול לטקסט
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.voice:
        await update.message.reply_text("לא הצלחתי להבין את ההודעה.")
        return

    voice: Voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tmp_file:
        await file.download_to_drive(custom_path=tmp_file.name)
        tmp_path = tmp_file.name

    # ממיר את הקובץ לטקסט באנגלית
    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            await update.message.reply_text(f"You said: {text}")
            # כאן אפשר להוסיף לוגיקת תיקון שגיאות בעתיד
        except sr.UnknownValueError:
            await update.message.reply_text("I couldn't understand what you said.")
        except sr.RequestError as e:
            await update.message.reply_text(f"Speech recognition error: {e}")

    os.remove(tmp_path)


# פונקציית הפעלה
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
