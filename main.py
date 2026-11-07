import os
import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYSTEM_PROMPT = "Ты — профессиональный редактор. Твоя задача — исправлять грамматические, орфографические и стилистические ошибки в тексте пользователя. Улучшай формулировки, делай текст более естественным и профессиональным. Сохраняй исходный смысл. Выдавай ТОЛЬКО исправленный текст, без своих комментариев и приветствий."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    user_text = message.text
    if not user_text:
        return

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat", 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        bot.reply_to(message, ai_response)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# --- Веб-сервер для Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Запускаем сервер в фоне
threading.Thread(target=run_server, daemon=True).start()

print("Бот запущен...")
bot.polling(none_stop=True)
