
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7836616724:AAEAfgKxr70dUq0xzubfLqScjE0IycBItXY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ADMINS = ['mtatarinova']

content = {
    "entry_instructions": (
        "*Адрес квартиры - Декабристов д. 93 кв. 32, подъезд 2, этаж 3*.\n"
        "Как подъедете к дому, найдите 2️⃣ подъезд, вход со стороны двора, на домофоне наберите номер квартиры 3️⃣2️⃣. "
        "Подождите 1-2 звонка, дверь подъезда откроется. Поднимитесь на 3️⃣ этаж. Рядом с квартирой установлен сейф с ключами.\n\n"
        "Для того, что открыть сейф опустите шторку, наберите код 2️⃣4️⃣7️⃣0️⃣, нажмите рычажок, который находится по левую руку, "
        "бокс откроется. После того, как заберете ключ, закройте крышку бокса, сбейте цифры в хаотичном порядке и поднимите шторку"
    ),
    "wifi": "Доступ к сети 🛜: логин TATTELECOM_3F91, пароль UENKN7DJ",
    "rules": (
        "*После заселения в течение 30 минут*\n"
        "- внести залог (страховой депозит) в размере 3000 рублей перечислением на карту 89030928588 Т Банк с указанием в примечании платежа «Залог»).\n"
        "Залог возвращается после уборки, в течение 4 часов после выезда гостей и проверки квартиры, в случае отсутствия нарушений правил проживания и признаков повреждения имущества.\n"
        "✔️К нарушениям относятся: порча или кража имущества (мебели, техники, посуды, текстиля), нарушение правил соблюдения тишины (с 22:00 до 7:00), признаки курения в арендованной квартире и нахождение посторонних лиц, не согласованных при заселении\n"
        "✔️В квартире запрещены любые виды курения (используйте для этого специально отведённые места). Размер штрафа за курение равен сумме залога.\n"
        "✔️Не оставляйте мусор в местах общего пользования: в подъезде или лестничной площадке: это нарушает правила пожарной безопасности. При уходе из квартиры выключайте воду, свет и бытовые электроприборы.\n"
        "✔️В квартире запрещено несогласованное проживание с любыми животными.\n"
        "✔️По всем вопросам можно обращаться по номеру телефона 89030928588 Марина"
    ),
    "tech_info": "Этой информации пока нет"
}

guest_chat_ids = set()

class EditStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_text = State()
    waiting_for_broadcast = State()

def guest_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Инструкция по заезду", "Wi-Fi")
    keyboard.add("Правила проживания", "Инфо по технике")
    keyboard.add("Связаться с хозяином")
    return keyboard

def admin_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Изменить инструкцию по заезду", "Изменить Wi-Fi")
    keyboard.add("Изменить правила проживания", "Изменить инфо по технике")
    keyboard.add("Рассылка гостям")
    keyboard.add("Выйти из админ-панели")
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    guest_chat_ids.add(message.chat.id)
    welcome_text = (
        "Добро пожаловать! Я бот для гостей апартаментов.\n\n"
        "Выберите нужный пункт меню:"
    )
    await message.answer(welcome_text, reply_markup=guest_menu())

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.username not in ADMINS:
        await message.answer("У вас нет доступа к админ-панели.")
        return
    await message.answer("Добро пожаловать в админ-панель. Выберите действие:",
                         reply_markup=admin_menu())

@dp.message_handler(lambda message: message.from_user.username in ADMINS, content_types=types.ContentTypes.TEXT)
async def admin_commands(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "Изменить инструкцию по заезду":
        await state.update_data(field="entry_instructions")
        await EditStates.waiting_for_text.set()
        await message.answer("Отправьте новый текст для инструкции по заезду:")
    elif text == "Изменить Wi-Fi":
        await state.update_data(field="wifi")
        await EditStates.waiting_for_text.set()
        await message.answer("Отправьте новый текст для Wi-Fi:")
    elif text == "Изменить правила проживания":
        await state.update_data(field="rules")
        await EditStates.waiting_for_text.set()
        await message.answer("Отправьте новый текст для правил проживания:")
    elif text == "Изменить инфо по технике":
        await state.update_data(field="tech_info")
        await EditStates.waiting_for_text.set()
        await message.answer("Отправьте новый текст для информации по технике:")
    elif text == "Рассылка гостям":
        await EditStates.waiting_for_broadcast.set()
        await message.answer("Отправьте текст для рассылки гостям:")
    elif text == "Выйти из админ-панели":
        await state.finish()
        await message.answer("Вы вышли из админ-панели.", reply_markup=guest_menu())
    else:
        await message.answer("Выберите действие из меню админ-панели.", reply_markup=admin_menu())

@dp.message_handler(state=EditStates.waiting_for_text, content_types=types.ContentTypes.TEXT)
async def process_edit_text(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    field = user_data.get("field")
    if field in content:
        content[field] = message.text
        await message.answer(f"Текст для *{field}* обновлен.", parse_mode="Markdown", reply_markup=admin_menu())
    else:
        await message.answer("Ошибка обновления. Попробуйте снова.", reply_markup=admin_menu())
    await state.finish()

@dp.message_handler(state=EditStates.waiting_for_broadcast, content_types=types.ContentTypes.TEXT)
async def process_broadcast(message: types.Message, state: FSMContext):
    broadcast_text = message.text
    count = 0
    for chat_id in guest_chat_ids:
        try:
            await bot.send_message(chat_id, f"[Рассылка]\n{broadcast_text}")
            count += 1
        except Exception as e:
            logging.error(f"Ошибка при отправке в чат {chat_id}: {e}")
    await message.answer(f"Рассылка отправлена {count} гостям.", reply_markup=admin_menu())
    await state.finish()

@dp.message_handler(lambda message: message.text in ["Инструкция по заезду", "Wi-Fi", "Правила проживания", "Инфо по технике", "Связаться с хозяином"])
async def guest_menu_handler(message: types.Message):
    txt = message.text
    if txt == "Инструкция по заезду":
        await message.answer(content["entry_instructions"], parse_mode="Markdown")
    elif txt == "Wi-Fi":
        await message.answer(content["wifi"])
    elif txt == "Правила проживания":
        await message.answer(content["rules"], parse_mode="Markdown")
    elif txt == "Инфо по технике":
        await message.answer(content["tech_info"])
    elif txt == "Связаться с хозяином":
        await message.answer("Ваше сообщение отправлено хозяину. Спасибо!")
    else:
        await message.answer("Выберите пункт из меню.", reply_markup=guest_menu())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)