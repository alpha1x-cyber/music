# api/index.py
from flask import Flask, request, send_file
import telebot
import yt_dlp
import json
import os
import requests
from io import BytesIO

app = Flask(__name__)
BOT_TOKEN = '7732102076:AAFlVQQ7lAFDqs9KvNzOJcDz5ArTMBRiF2A'
bot = telebot.TeleBot(BOT_TOKEN)

# معلومات المطور
DEVELOPER_NAME = "المهندس البرمجيات ياسين طه"
DEVELOPER_USERNAME = "@CODE_X010"

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
🎵 مرحباً بك في بوت الموسيقى!

• ما عليك سوى إرسال اسم الأغنية وسأقوم 

👨‍💻 معلومات المطور:
• الاسم: {DEVELOPER_NAME}
• المعرف: @{DEVELOPER_USERNAME}

📌 يمكنك استخدام البوت في المجموعات والمحادثات الخاصة
"""
    bot.reply_to(message, welcome_text)

def save_to_json(data, filename='data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def load_from_json(filename='data.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info['title']
        return audio_url, title

@bot.message_handler(func=lambda message: True)
def search_song(message):
    try:
        bot.reply_to(message, "🔍 جاري البحث...")
        query = message.text
        search_url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(search_url)
        
        video_id = response.text.split('"videoId":"')[1].split('"')[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        bot.reply_to(message, "⏳ جاري التحميل...")
        audio_url, title = download_audio(url)
        
        audio_data = requests.get(audio_url).content
        audio_io = BytesIO(audio_data)
        audio_io.name = f"{title}.mp3"
        
        bot.send_audio(message.chat.id, audio_io, caption=f"🎵 {title}")
        
    except Exception as e:
        bot.reply_to(message, "❌ عذراً، حدث خطأ في معالجة طلبك")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK'

@app.route('/')
def home():
    return 'Bot is running'

if __name__ == '__main__':
    app.run()