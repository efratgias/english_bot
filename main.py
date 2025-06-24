import os
import logging
import random
import difflib
import tempfile

from telegram import Update, Voice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import torch
import whisper
from gtts import gTTS
from pydub import AudioSegment

# הגדרת רשימת משפטים
sentences = [
    "The quick brown fox jumps over the lazy dog",
    "Practice makes perfect",
    "She sells seashells by the seashore",
    "Better late than never",
    "A journey of a thousand miles begins with a single step"
]

# אתחול מודל ההמרה מדיבור לטקסט
model = whisper.load_model("base")

# הפעלת לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# משתנה גלובלי לשמירת המשפט הנוכחי
user_sentences = {}

# שלב 1: הפעלת הבוט עם משפט חדש
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sentence = random.choice(sentences)
    user_sentences[user_id] = sentence

    # יצירת אודיו עם gTTS
    tts = gTTS(sentence)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        audio_path = f.name

    # שליחת המשפט + קובץ קול
    await update.message.reply_text(f"Please repeat this sentence:\n\n{sentence}")
    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(audio_path, 'rb'))

# שלב 2: קבלת ההקלטה מהמשתמש
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sentences:
        await update.message.reply_text("Please start with /start")
        return

    sentence = user_sentences[user_id]

    voice: Voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    ogg_path = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg").name
    wav_path = ogg_path.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_path)

    # המרה ל-WAV
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

    # זיהוי טקסט
    result = model.transcribe(wav_path)
    recognized = result['text'].strip()

    # חישוב דיוק
    ratio = difflib.SequenceMatcher(None, sentence.lower(), recognized.lower()).ratio()
    score = int(ratio * 100)

    await update.message.reply_text(
        f"✅ You said: {recognized}\n🎯 Original: {sentence}\n📊 Pronunciation accuracy: {score}%\n\nSend a new voice message to try again or type /start for a new sentence."
    )

# הפעלת הבוט
if __name__ == '__main__':
    TOKEN = os.environ['BOT_TOKEN']
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()
