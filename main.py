from telebot import TeleBot, types

bot = TeleBot("BOT_TOKEN")
MINI_APP_URL = "https://puffashop.netlify.app"  # реальный HTTPS-адрес твоего веб-приложения
MANAGER = "https://t.me/seeftf"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    webapp_btn = types.InlineKeyboardButton(
        text="🛒 Открыть каталог",
        web_app=types.WebAppInfo(MINI_APP_URL)
    )
    manager_btn = types.InlineKeyboardButton(
        text="💬 Связаться с менеджером",
        url=MANAGER
    )
    markup.add(webapp_btn)
    markup.add(manager_btn)

    text = """
👋 <b>Добро пожаловать в PuffaShop!</b>

💨 Официальный магазин жидкостей для электронных сигарет.

Здесь вы можете:
• 🛒 оформить заказ
• 🍓 посмотреть весь ассортимент
• 🔥 узнать о новинках и поступлениях
• 💬 связаться с менеджером

━━━━━━━━━━━━━━━

📦 Только оригинальная продукция
⚡ Актуальное наличие каждый день
🚚 Быстрая обработка заказов

"""

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=markup
    )

bot.infinity_polling()