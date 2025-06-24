import os
import random
import tempfile
import difflib
import speech_recognition as sr
from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# משפטים לשיפור האנגלית
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

    tts = gTTS(sentence)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        await update.message.reply_voice(voice=open(f.name, "rb"))
        os.remove(f.name)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sentences:
        await update.message.reply_text("Please start with /start to get a sentence.")
        return

    sentence = user_sentences[user_id]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as voice_file:
        file = await context.bot.get_file(update.message.voice.file_id)
        await file.download_to_drive(voice_file.name)

    audio_path = voice_file.name
    wav_path = audio_path.replace(".ogg", ".wav")

    os.system(f"ffmpeg -i {audio_path} {wav_path} -y")
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        result = recognizer.recognize_google(audio)
        ratio = difflib.SequenceMatcher(None, sentence.lower(), result.lower()).ratio()
        accuracy = round(ratio * 100)
        await update.message.reply_text(f"✅ Accuracy: {accuracy}%\nYou said: \"{result}\"")
    except sr.UnknownValueError:
        await update.message.reply_text("Sorry, I couldn't understand your pronunciation.")
    except sr.RequestError:
        await update.message.reply_text("There was an error with the speech recognition service.")

    os.remove(audio_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()
