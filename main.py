import os
import random
import tempfile
import difflib
import speech_recognition as sr
from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# משפטים לשיפור ההגייה
SENTENCES = [
    "I have never been to New York.",
    "She enjoys learning English every day.",
    "Can you repeat that, please?",
    "Practice makes perfect.",
    "It’s never too late to start."
]

user_sentences = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence = random.choice(SENTENCES)
    user_id = update.effective_user.id
    user_sentences[user_id] = sentence

    await update.message.reply_text(f"🗣 Repeat this sentence:\n\n\"{sentence}\"")

    # צור קובץ קול מהמשפט ושלח למשתמש
    tts = gTTS(sentence)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        await update.message.reply_voice(voice=open(f.name, "rb"))
    os.remove(f.name)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sentences:
        await update.message.reply_text("Please start first by sending /start")
        return

    # הורד את הודעת הקול הזמנית
    voice = await update.message.voice.get_file()
    ogg_path = f"{user_id}.ogg"
    wav_path = f"{user_id}.wav"
    await voice.download_to_drive(ogg_path)

    # המר ל-wav (רנדר תומך בזה ב-Ffmpeg מותקן)
    os.system(f"ffmpeg -i {ogg_path} -ar 16000 -ac 1 {wav_path}")

    # זיהוי דיבור
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        recognized_text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        recognized_text = ""

    # ניקוי קבצים זמניים
    os.remove(ogg_path)
    os.remove(wav_path)

    # השוואה בין המשפט שנשלח למה שהמשתמש אמר
    expected = user_sentences[user_id]
    seq = difflib.SequenceMatcher(None, expected.lower(), recognized_text.lower())
    score = round(seq.ratio() * 100)

    await update.message.reply_text(
        f"✅ You said: \"{recognized_text}\"\n🎯 Target: \"{expected}\"\n📊 Accuracy: {score}%"
    )

if __name__ == "__main__":
    import asyncio

    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    asyncio.run(app.run_polling())
