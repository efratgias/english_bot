import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import torch
import whisper
from gtts import gTTS
from pydub import AudioSegment
import difflib

# הגדרת מודל whisper
model = whisper.load_model("base")

# אחסון המשפט הנוכחי
user_sentences = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence = "The quick brown fox jumps over the lazy dog"
    user_id = update.effective_user.id
    user_sentences[user_id] = sentence
    
    await update.message.reply_text(sentence)

    # הקראת המשפט
    tts = gTTS(sentence)
    tts.save("sentence.mp3")
    audio = AudioSegment.from_file("sentence.mp3")
    audio.export("sentence.ogg", format="ogg")
    
    with open("sentence.ogg", "rb") as voice:
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sentence = user_sentences.get(user_id)
    if not sentence:
        await update.message.reply_text("Please start with /start")
        return

    file = await context.bot.get_file(update.message.voice.file_id)
    file_path = "user_voice.ogg"
    await file.download_to_drive(file_path)

    audio = AudioSegment.from_file(file_path)
    wav_path = "user_voice.wav"
    audio.export(wav_path, format="wav")

    result = model.transcribe(wav_path)
    spoken = result["text"]

    # חישוב אחוז דיוק
    ratio = difflib.SequenceMatcher(None, sentence.lower(), spoken.lower()).ratio()
    score = int(ratio * 100)

    await update.message.reply_text(f"Your pronunciation score: {score}%")
    await update.message.reply_text("Send the voice again or type /start for a new sentence")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    application.run_polling()
