import json
import os
from telebot import TeleBot, types

bot = TeleBot(os.environ["BOT_TOKEN"])
MINI_APP_URL = "https://puffashop.netlify.app"
MANAGER = "https://t.me/seeftf"

# Путь к файлу хранения данных пользователей
USERS_FILE = "users_data.json"

# ─── Утилиты для хранения данных ────────────────────────────────────────────

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(data: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_user(message: types.Message):
    """Сохраняет/обновляет информацию о пользователе при каждом обращении."""
    users = load_users()
    uid = str(message.from_user.id)
    user = message.from_user

    existing = users.get(uid, {})

    # Собираем всю доступную информацию
    users[uid] = {
        "id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": f"@{user.username}" if user.username else "",
        "language_code": user.language_code or "",
        "is_bot": user.is_bot,
        "is_premium": getattr(user, "is_premium", False),
        "chat_id": message.chat.id,
        "chat_type": message.chat.type,
        "first_seen": existing.get("first_seen", message.date),
        "last_seen": message.date,
        "message_count": existing.get("message_count", 0) + 1,
        "commands_used": existing.get("commands_used", []),
    }

    # Фиксируем, какие команды использовал
    if message.text and message.text.startswith("/"):
        cmd = message.text.split()[0]
        cmds = users[uid]["commands_used"]
        if cmd not in cmds:
            cmds.append(cmd)

    save_users(users)

# ─── Команды ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start(message):
    record_user(message)

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


@bot.message_handler(commands=['getid'])
def get_id(message):
    """Показывает ID текущего чата и пользователя."""
    record_user(message)

    text = (
        f"🆔 <b>Информация об ID</b>\n\n"
        f"👤 <b>Ваш user ID:</b> <code>{message.from_user.id}</code>\n"
        f"💬 <b>ID этого чата:</b> <code>{message.chat.id}</code>\n"
        f"📌 <b>Тип чата:</b> {message.chat.type}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


@bot.message_handler(commands=['getusers'])
def get_users(message):
    """Показывает всю собранную информацию о пользователях бота."""
    record_user(message)

    users = load_users()

    if not users:
        bot.send_message(message.chat.id, "📭 Пока нет данных о пользователях.")
        return

    lines = [f"👥 <b>Пользователи бота</b> — всего: {len(users)}\n"]

    for uid, u in users.items():
        # Форматируем дату первого и последнего визита
        from datetime import datetime, timezone
        first = datetime.fromtimestamp(u['first_seen'], tz=timezone.utc).strftime("%d.%m.%Y %H:%M")
        last  = datetime.fromtimestamp(u['last_seen'],  tz=timezone.utc).strftime("%d.%m.%Y %H:%M")

        full_name = f"{u['first_name']} {u['last_name']}".strip() or "—"
        username  = u['username'] or "—"
        premium   = "✅" if u.get('is_premium') else "❌"
        lang      = u.get('language_code') or "—"
        cmds      = ", ".join(u.get('commands_used', [])) or "—"

        lines.append(
            f"━━━━━━━━━━━━━━━\n"
            f"👤 <b>{full_name}</b> {username}\n"
            f"🆔 ID: <code>{u['id']}</code>  |  💬 Chat: <code>{u['chat_id']}</code>\n"
            f"🌐 Язык: {lang}  |  ⭐ Premium: {premium}\n"
            f"📊 Сообщений: {u['message_count']}\n"
            f"🗂 Команды: {cmds}\n"
            f"📅 Первый визит: {first}\n"
            f"🕐 Последний визит: {last}"
        )

    full_text = "\n".join(lines)

    # Telegram ограничивает сообщение до 4096 символов — разбиваем если нужно
    max_len = 4096
    for i in range(0, len(full_text), max_len):
        bot.send_message(message.chat.id, full_text[i:i + max_len], parse_mode="HTML")


# ─── Запуск ─────────────────────────────────────────────────────────────────

bot.infinity_polling()
