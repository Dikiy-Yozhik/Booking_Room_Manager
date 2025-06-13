import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# === Ваш Telegram токен ===
TELEGRAM_TOKEN = '8111991124:AAGDOZnAqr5Kl9ZT4pD9s-VFbJ31Mmu4VFs'
# URL для локального Ollama API (по умолчанию)
OLLAMA_API_URL = "http://localhost:11434/api/chat"

ROLES = {
    "Чингисхан": "представь что ты Чингисхан - основатель монгольской империи из 13 века. веди диалог как это делал бы он. Говори на русском языке. веди себя исторически достоверно. Отвечай не слишком длинно",
    "Александр Невский": "представь что ты Александр Невский - великий князь киевский и владимирский из 13 века. веди диалог как это делал бы он. Говори на русском языке. веди себя исторически достоверно. Отвечай не слишком длинно",
    "Иван Калита": "представь что ты Иван Калита - великий князь московский и владимирский из 14 века. веди диалог как это делал бы он. Говори на русском языке. веди себя исторически достоверно. Отвечай не слишком длинно",
    "Батый": "представь что ты Батый - Внук Чингисхаана и сын Джучи, основатель и хан золотой орды. веди диалог как это делал бы он. Говори на русском языке. веди себя исторически достоверно. Отвечай не слишком длинно"
}

user_roles = {}
conversation_history = {}

logging.basicConfig(level=logging.INFO)

def generate_ollama_response(user_message, system_prompt, history=None, model="llama3"):
    if history is None:
        history = []

    # ollama chat-style prompt
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    try:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)

        if response.status_code == 200:
            res = response.json()
            # Ollama отвечает либо сразу (message: {content:...}), либо (message: {content:...}, done: True)
            reply = res.get("message", {}).get("content", "").strip()
            if not reply:
                reply = "Извините, не удалось сгенерировать ответ."
            history.append({'role': 'user', 'content': user_message})
            history.append({'role': 'assistant', 'content': reply})
            return reply, history
        else:
            logging.error(f"Ollama API error: {response.text}")
            return "Извините, возникла техническая проблема с Ollama API.", history
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return f"Ошибка при обращении к Ollama: {str(e)}", history


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Клавиатура теперь остаётся на экране постоянно (one_time_keyboard=False)
    keyboard = [[role] for role in ROLES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text('Привет! Выбери роль для общения:', reply_markup=reply_markup)


async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Если сообщение - это название существующей роли, меняем роль
    if text in ROLES:
        user_roles[user_id] = text
        conversation_history[user_id] = []  # Очищаем историю при смене роли
        await update.message.reply_text(f"Теперь я - {text}. Спрашивай!")
        return  # Прерываем дальнейшую обработку

    # Если роль ещё не выбрана, просим выбрать
    if user_id not in user_roles:
        await start(update, context)
        return

    # Если это обычное сообщение - обрабатываем с текущей ролью
    role = user_roles[user_id]
    role_prompt = ROLES[role]
    user_message = text
    history = conversation_history.get(user_id, [])

    # Отправляем действие "печатает..."
    await update.message.chat.send_action(action="typing")

    # Генерируем ответ через Ollama
    bot_reply, updated_history = generate_ollama_response(
        user_message=user_message,
        system_prompt=role_prompt,
        history=history
    )

    # Обновляем историю и отправляем ответ
    conversation_history[user_id] = updated_history
    await update.message.reply_text(bot_reply)

async def reset_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_roles.pop(user_id, None)
    conversation_history.pop(user_id, None)
    await start(update, context)

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_role))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    print("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
