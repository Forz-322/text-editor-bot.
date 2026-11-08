import os
import telebot
import requests
from flask import Flask, request

# --- Налаштування ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
# URL вашого сервісу на Render (додамо пізніше в налаштуваннях)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL') 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

SYSTEM_PROMPT = """Відредагуй мій текст так, щоб він звучав грамотно, природно та переконливо. Збережи мою основну думку й усі важливі аргументи, але покращ формулювання, логіку та структуру речень.

Використовуй сучасну українську мову, уникай канцеляризмів, повторів і надмірно складних конструкцій.

Тон тексту має бути впевненим, аргументованим і дипломатичним. Якщо потрібно відстояти мою позицію — зроби це чітко та наполегливо, але без образ, агресії чи зайвих емоцій.

Не змінюй зміст моїх слів і не додавай вигаданих фактів. Текст має виглядати так, ніби його написала реальна людина, а не штучний інтелект.

Зроби готовий варіант, який можна одразу скопіювати та надіслати."""

# Обробник повідомлень (залишається без змін)
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

# --- Webhook частина ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    # Цей маршрут потрібен для перевірки, що сервіс живий
    return "Bot is running", 200

if __name__ == "__main__":
    # Видаляємо старий вебхук (якщо був) і ставимо новий
    bot.remove_webhook()
    # Встановлюємо вебхук на адресу вашого сервісу
    bot.set_webhook(url=WEBHOOK_URL + TELEGRAM_TOKEN)
    
    # Запускаємо Flask сервер на порту, який надає Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
