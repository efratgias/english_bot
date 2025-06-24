import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import torch
import whisper
from gtts import gTTS
from pydub import AudioSegment
import uuid

# טען את מודל whisper
model = whisper.load_model("base")

# משפט לדוגמה לתרגול
practice_sentences = [
    "The quick brown fox jumps over the lazy dog",
    "She sells seashells by the seashore",
    "Practice makes perfect",
    "How are you doing today?",
    "This is a test sentence"
]
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sentence = practice_sentences[torch.randint(0, len(practice_sentences), (1,)).item()]
    user_sessions[user_id] = sentence

    # שליחת טקסט
    await update.message.reply_text(f"Repeat this sentence:\n\n📢 {sentence}")

    # יצירת קול ושליחה
    tts = gTTS(sentence)
    filename = f"{uuid.uuid4()}.mp3"
    tts.save(filename)
    await update.message.reply_voice(voice=open(filename, "rb"))
    os.remove(filename)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start to get a sentence to repeat.")
        return

    sentence = user_sessions[user_id]

    # הורדת ההודעה הקולית
    file = await context.bot.get_file(update.message.voice.file_id)
    file_path = f"{uuid.uuid4()}.ogg"
    await file.download_to_drive(file_path)

    # המרה ל־wav
    audio = AudioSegment.from_file(file_path)
    wav_path = f"{uuid.uuid4()}.wav"
    audio.export(wav_path, format="wav")
    os.remove(file_path)

    # זיהוי דיבור
    result = model.transcribe(wav_path)
    spoken_text = result["text"]
    os.remove(wav_path)

    # חישוב דיוק
    original_words = sentence.lower().split()
    spoken_words = spoken_text.lower().split()
    match = sum(1 for a, b in zip(original_words, spoken_words) if a == b)
    score = int((match / len(original_words)) * 100)

    await update.message.reply_text(f"🗣 You said: {spoken_text}\n✅ Pronunciation Score: {score}%\n\nType /start to try another!")

if __name__ == '__main__':
    import asyncio
    from telegram.ext import Application

    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()
