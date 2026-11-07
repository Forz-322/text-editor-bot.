import os
import telebot
import requests

# Берем ключи из настроек сервера (об этом ниже)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Наша строгая инструкция для DeepSeek
SYSTEM_PROMPT = "Ты — профессиональный редактор. Твоя задача — исправлять грамматические, орфографические и стилистические ошибки в тексте пользователя. Улучшай формулировки, делай текст более естественным и профессиональным. Сохраняй исходный смысл. Выдавай ТОЛЬКО исправленный текст, без своих комментариев и приветствий."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Отправляем пользователю статус "печатает..."
    bot.send_chat_action(message.chat.id, 'typing')
    
    user_text = message.text
    if not user_text:
        return

    # Запрос к DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-flash", # Самая дешевая и быстрая модель
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
        
        # Получаем ответ от ИИ
        ai_response = result['choices'][0]['message']['content']
        
        # Отправляем ответ пользователю
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обработке текста. Проверьте баланс или ключ. Ошибка: {e}")

# Запуск бота
bot.polling(none_stop=True)
