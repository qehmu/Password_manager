import asyncio
import random
import sqlite3
import time
import tokens

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import (KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, Message)

dp = Dispatcher(storage=MemoryStorage())
TOKEN = tokens.token
bot = Bot(token=TOKEN)
# Объявляем список символов, из которых будет генерироваться пароль
chars = tokens.chars

class Password(StatesGroup):
    set_enter_pass = State()
    set_enter_pass_2 = State()
    add_pass = State()
    delete_pass = State()
    generate = State()
    set_pass = State()
    check_pass = State()
    set_pass_2 = State()
    start_cmd = State()
    commands = State()


# Клавиатура
clear_kb = ReplyKeyboardRemove()
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить пароль")],
        [KeyboardButton(text="Удалить пароль")],
        [KeyboardButton(text="Сгенерировать пароль")],
        [KeyboardButton(text="Посмотреть пароли")]
    ],
    resize_keyboard=True
)

# Создаем соединение с базой данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу для хранения паролей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    password_enter TEXT,
    password_1 TEXT,
    password_2 TEXT,
    password_3 TEXT,
    password_4 TEXT,
    password_5 TEXT
)
''')
conn.commit()
msg = ['/add', '/help', '/generate_pass', '/check_passwords', '/delete', '/enter_pass', '/recommend', '/clear_list']

# Команда старт, обрабатывает идентификационный номер пользователя, и сравнивает его наличие в базе данных
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    await message.answer("Привет! Я твой менеджер паролей.")
    time.sleep(1)
    cursor.execute("SELECT password_enter FROM users WHERE id = ?", (user_id,))
    result_2 = cursor.fetchone()
    if result_2 is None or result_2[0] is None or result_2[0] == '':
        await state.set_state(Password.set_enter_pass)
        await message.answer("Перед началом пользования, задайте любой пароль, введя его сюда.")
    elif result_2 is not None:
        await message.answer(
            "У вас уже установлен мастер-пароль, поэтому предлагаю ознакомиться с моими командами:\n1. /generate_pass - Сгенерировать пароль\n2. /add - Добавить пароль в список\n3. /delete - Удалить пароль из списка\n4. /set_enter_pass - Установить новый пароль для списка паролей\n5. /check_passwords - Посмотреть список паролей\n6. /recommend - Показать рекомендации к обороту данных и паролей\n7. /help - Показать возможности бота")
        await state.clear()

# Обработчик сообщений в случае не прохождения проверки пользователя на нахождение в базе данных
@dp.message(Password.set_enter_pass)
async def login_set_enter_pass(message: Message, state: FSMContext):
    enter_pass = message.text
    user_id = message.from_user.id
    if enter_pass == msg[0 - 7]:
        await message.answer("Команда не является паролем. Введите пароль.")
    elif enter_pass != msg[0 - 7]:
        cursor.execute("UPDATE users SET password_enter = ? WHERE id = ?", (enter_pass, user_id))
        await message.delete()
        conn.commit()
        await message.answer("Хорошо, сохраняю ваш пароль...", reply_markup=clear_kb)
        await state.clear()
        await message.answer(
            "С моей помощью вы можете:\n1. /generate_pass - Сгенерировать пароль\n2. /add - Добавить пароль в список\n3. /delete - Удалить пароль из списка\n4. /set_enter_pass - Установить новый пароль для списка паролей\n5. /check_passwords - Посмотреть список паролей\n6. /recommend - Показать рекомендации к обороту данных и паролей\n7. /help - Показать возможности бота\n8. /clear_list - Очистить список паролей")

# Команда /help
@dp.message(Command("help"))
async def getHelp(message: Message):
    await message.answer(
        "Мои команды:\n1. /generate_pass - Сгенерировать пароль\n2. /add - Добавить пароль в список\n3. /delete - Удалить пароль из списка\n4. /set_enter_pass - Установить новый пароль для списка паролей\n5. /check_passwords - Посмотреть список паролей\n6. /recommend - Показать рекомендации к обороту данных и паролей\n7. /help - Показать возможности бота\n8. /clear_list - Очистить список паролей")

# Команда /recommend
@dp.message(Command("recommend"))
async def recommendations(message: Message, state: FSMContext):
    await message.answer(
        f"Хорошо, вот мои рекомендации по созданию паролей.\nhttps://www.kaspersky.ru/resource-center/threats/how-to-create-a-strong-password\nhttps://nabiraem.ru/blog/articles/advices/kak-pravilno-podobrat-parol--29")
    await state.clear()

# Команда /clear_list, очищающая все пароли в базе данных, находит пользователя по user_id
@dp.message(Command("clear_list"))
async def clear_password_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute(
        f'UPDATE users SET password_1 = NULL, password_2 = NULL, password_3 = NULL, password_4 = NULL, password_5 = NULL WHERE id = ?',
        (user_id,))
    cursor.fetchone()
    conn.commit()
    await message.answer("Ваш список паролей очищен!")
    await state.clear()

# Команда /cl_ent_pass
@dp.message(Command("cl_ent_pass"))
async def clear_enter_pass(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute(f'UPDATE users SET password_enter = NULL WHERE id = ?', (user_id,))
    cursor.fetchone()
    conn.commit()
    await message.answer("Ваш enter_pass очищен!")
    await message.answer("Найдена пасхалка. А ты молодец!")
    await state.clear()

# Команда /set_enter_pass, задающая новый пароль для просмотра списка паролей
@dp.message(Command("set_enter_pass"))
async def command_set_enter_pass(message: Message, state: FSMContext):
    await message.answer(
        "Для установления нового пароля необходимо его ввести. Помните, что паролю лучше быть длинным и сложным. Читать про сложность паролей: /recommend")
    await state.set_state(Password.set_enter_pass_2)

# Обработчик сообщений с команды /set_enter_pass
@dp.message(Password.set_enter_pass_2)
async def set_enter_pass_2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    enter_pass = message.text
    if enter_pass == '/recommend':
        await message.answer(
            "Хорошо, вот мои рекомендации по созданию паролей."
            "\nhttps://www.kaspersky.ru/resource-center/threats/how-to-create-a-strong-password"
            "\nhttps://nabiraem.ru/blog/articles/advices/kak-pravilno-podobrat-parol--29"
            "\nhttps://habr.com/ru/companies/ua-hosting/articles/273373/")
    await message.delete()
    await message.answer("Ваш пароль для списка изменен.", reply_markup=clear_kb)
    await state.clear()
    cursor.execute(f'UPDATE users SET password_enter = ? WHERE id = ?', (enter_pass, user_id))
    conn.commit()

# Команда /add
@dp.message(Command("add"))
async def add_pass_enter(message: Message, state: FSMContext):
    await state.set_state(Password.add_pass)
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    await message.answer("Пришлите пароль, который хотите добавить.", reply_markup=clear_kb)

# Обработчик команды /add, добавляющий текст сообщения в список паролей
@dp.message(Password.add_pass)
async def add_pass(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute('SELECT password_1, password_2, password_3, password_4, password_5 FROM users WHERE id = ?',
                   (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO users (password_1) VALUES (?)', (message.text,))
    else:
        cursor.execute('SELECT password_5 FROM users WHERE id = ?', (user_id,))
        result_verify_pass = cursor.fetchone()
        if result_verify_pass is not None and result_verify_pass[0] is not None and result_verify_pass[0] != 'null':
            await message.answer(
                "Предупреждение! Превышен лимит 5 хранимых паролей. Все далее добавленные пароли будут перезаписываться в пароль с номером 5.")
        for i in range(1, 6):
            if row[i - 1] is None:
                cursor.execute(f'UPDATE users SET password_{i} = ? WHERE id = ?', (message.text, user_id))
                break
    conn.commit()
    await message.delete()
    await message.answer(f"Пароль добавлен.")
    await state.clear()

# Команда /generate_pass
@dp.message(Command("generate_pass"))
async def generate_pass(message: Message, state: FSMContext):
    await state.set_state(Password.generate)
    await message.answer("Введите желаемое количество символов в пароле (от 3 до 30):", reply_markup=clear_kb)

# Обработчик команды /generate_pass, может генерировать числа от 3 до 30, условия создания можно изменить, на допустим 1-30 символов.
@dp.message(Password.generate)
async def generate_pass_length(message: Message, state: FSMContext):
    length_of_generated_pass = int(message.text)
    if 3 <= length_of_generated_pass <= 30:
        password_sym = ''.join(random.choice(chars) for _ in range(length_of_generated_pass))
        await message.answer(f"Вот ваш сгенерированный пароль: {password_sym}\nХотите добавить его в список паролей?",
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[
                                     [KeyboardButton(text="Добавить")],
                                     [KeyboardButton(text="Не добавлять")]
                                 ],
                                 resize_keyboard=True,
                                 one_time_keyboard=True
                             ))
        await state.set_state(Password.set_pass)
        await state.update_data(name=password_sym)
    else:
        await message.answer("Длина пароля должна быть от 3 до 30 символов. Попробуйте снова.")
        await state.clear()

# Обработчик решения пользователя о добавлении в список его сгенерированного пароля.
@dp.message(Password.set_pass)
async def add_generated_pass_2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "Добавить":
        user_data = await state.get_data()
        last_password = user_data.get('name')
        if last_password:
            cursor.execute('SELECT password_1, password_2, password_3, password_4, password_5 FROM users WHERE id = ?',
                           (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute('INSERT INTO users (password_1) VALUES (?)', (last_password,))
            else:
                for i in range(1, 6):
                    if row[i - 1] is None:
                        cursor.execute(f'UPDATE users SET password_{i} = ? WHERE id = ?', (last_password, user_id))
                        break
            conn.commit()
            await message.answer(f"Пароль '{last_password}' добавлен в список ваших паролей.")
        else:
            await message.answer("Ошибка: не удалось получить сгенерированный пароль.")
    else:
        await message.answer("Ошибка: пароль не будет добавлен в ваш список паролей.")

    await state.clear()

# Команда выдает все пароли пользователя, но перед этим определяет, есть ли у него мастер-пароль
@dp.message(Command("check_passwords"))
async def verify_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    conn.commit()
    cursor.execute("SELECT password_enter FROM users WHERE id = ?", (user_id,))
    result_verify_pass = cursor.fetchone()[0]
    if result_verify_pass == 'None':
        await message.answer("У вас не установлен пароль. Вы можете ввести его сюда, дабы установить пароль.")
        await state.set_state(Password.set_pass_2)
    else:
        await message.answer("Введите пароль, чтобы получить доступ к сохраненным паролям.")
        await state.set_state(Password.check_pass)

# Обработчик мастер-пароля, сравнивается со значением из базы данных, и если все верно, пользователь получает свой список паролей
@dp.message(Password.check_pass)
async def view_passwords(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT password_enter FROM users WHERE id = ?", (user_id,))
    check_entpass_2 = cursor.fetchone()
    check_entpass_2_xd = check_entpass_2[0]
    entered_pass = message.text
    if entered_pass == check_entpass_2_xd:
        cursor.execute("SELECT password_1, password_2, password_3, password_4, password_5 FROM users WHERE id = ?",
                       (user_id,))
        passwd = cursor.fetchone()
        if passwd:
            password_list = [f"Пароль {i + 1}: {pw}" for i, pw in enumerate(passwd) if pw is not None]
            if password_list:
                await message.answer("\n".join(password_list))
                conn.commit()
            else:
                await message.answer("У вас нет сохраненных паролей.")
    else:
        await message.answer("Ошибка. Неверный пароль, попробуйте еще раз.")
        await state.set_state(Password.check_pass)
    conn.commit()

# Обработчик предыдущей команды, сообщение, введенное в этом блоке кода, будет являтся мастер-паролем в будущем
@dp.message(Password.set_pass_2)
async def set_enter_pass(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE users SET password_enter = {message.text} WHERE id = ?", (user_id,))
    await state.clear()

# Команда /delete
@dp.message(Command("delete"))
async def delete_pass_enter(message: Message, state: FSMContext):
    await state.set_state(Password.delete_pass)
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    await message.answer("Введите номер пароля, который хотите удалить (1-5):", reply_markup=clear_kb)

# Обработчик команды /delete, обNULLяет значение заданного пароля
@dp.message(Password.delete_pass)
async def delete_pass(message: Message, state: FSMContext):
    user_id = message.from_user.id
    number = int(message.text)
    cursor.execute('SELECT password_1, password_2, password_3, password_4, password_5 FROM users WHERE id = ?',
                   (user_id,))
    result_db = cursor.fetchone()
    try:
        cursor.execute(f'SELECT password_{number} FROM users WHERE id = ?', (user_id,))
        check_num_of_pass = cursor.fetchone()[0]
        if any in result_db is None:
            await message.answer("У вас нет паролей, которые можно было бы удалить.")
            await state.clear()
            return
        if not check_num_of_pass:
            await message.answer(f"Пароль с номером {number} не существует! Попробуй снова.")
            await state.set_state(Password.delete_pass)
            return
        elif 1 <= number <= 5:
            cursor.execute(f'UPDATE users SET password_{number} = NULL WHERE id = ?', (user_id,))
            conn.commit()
            await message.answer(f"Пароль номер {number} удален.")
            await state.clear()
    except sqlite3.OperationalError:
        await message.answer("Не существует такого номера пароля. Существуют номера 1-5.")
        await state.set_state(Password.delete_pass)


async def main() -> None:
    bot_1 = Bot(TOKEN)
    await bot_1(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot_1)


if __name__ == "__main__":
    asyncio.run(main())
# На этом все.
# Менеджер паролей в одном файле, 330 строк. Работы завершены 7 Мая 2025 15:00