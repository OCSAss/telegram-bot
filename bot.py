
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from mcrcon import MCRcon

# --- Переменные окружения (Render) ---
TOKEN = os.getenv("7866697079:AAH1G1-t3kykuYZs9pRdjpvkJ52i-6JgkRI")  # Telegram токен
RCON_HOST = os.getenv("skyhaven.sosal.today")  # IP сервера
RCON_PASSWORD = os.getenv("")  # Пароль RCON
RCON_PORT = int(os.getenv("25575))  # Порт RCON, по умолчанию 25575

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DB_FILE = "whitelist.json"
user_states = {}  # временные состояния пользователей

# --- Работа с локальной базой ---
def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Команды бота ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Введите ник в игре:")
    user_states[message.from_user.id] = "waiting_nick"

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    # --- Шаг 1: ввод ника ---
    if state == "waiting_nick":
        nick = message.text.strip()
        data = load_data()

        if any(user.get("nick") == nick for user in data):
            await message.answer("❌ Такой ник уже зарегистрирован!")
            return

        user_states[user_id] = {"nick": nick}
        await message.answer("Введите ваше ФИО (необязательно):")

    # --- Шаг 2: ввод ФИО ---
    elif isinstance(state, dict):
        name = message.text.strip()
        data = load_data()
        nick = state["nick"]

        # --- Сохраняем в локальную базу ---
        data.append({
            "user_id": user_id,
            "nick": nick,
            "name": name
        })
        save_data(data)

        # --- Отправляем команду на сервер через RCON (TemporaryWhitelist) ---
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
                mcr.command(f"twhitelist add {nick}")
        except Exception as e:
            print("Ошибка RCON:", e)

        # --- Сообщение пользователю ---
        await message.answer(
            "✅ Вы успешно добавлены в whitelist!\n\n"
            "🙏 Спасибо за регистрацию!\n\n"
            "📥 Скачать сборку:\n"
            "https://drive.google.com/file/d/1G0BkfuP23grBZMvxUvogzvvDUFwb12MU/view?usp=drive_link\n\n"
            "📢 Наш Telegram канал:\n"
            "https://t.me/+DnXYWcoDR7YyMGMy"
        )

        user_states.pop(user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)