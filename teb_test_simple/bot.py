import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from database import init_db, user_get_by_tg_id, user_save
from services import (
    validate_age,
    validate_sex,
    validate_username,
    validate_name,
)

API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
session = init_db()


class Registration(StatesGroup):
    name = State()
    username = State()
    age = State()
    sex = State()


def get_keyboard_to_site() -> InlineKeyboardMarkup:
    link_keyboard = InlineKeyboardMarkup()
    link_keyboard.add(
        InlineKeyboardButton(
            text='Go to the site', 
            url=os.getenv('SITE_URL')
        )
    )
    return link_keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = user_get_by_tg_id(session, message.from_user.id)
    if user:
        link_keyboard = get_keyboard_to_site()
        await message.answer(f'Hello, {str(user)}!', reply_markup=link_keyboard)
        return
    await Registration.name.set()
    await message.answer(
        '''
        Hello, let's begin the registration!
        What is your name?
        ''')

@dp.message_handler(validate_name, state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['telegram_id'] = message.from_user.id
        data['name'] = message.text
    await Registration.next()
    await message.answer('What is your username?')

@dp.message_handler(lambda message: not validate_name(message), state=Registration.name)
async def process_incorrect_name(message: types.Message):
    return await message.reply('Name must be a string of 2 to 30 characters')

@dp.message_handler(validate_username, state=Registration.username)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    await Registration.next()
    await message.answer('How old are you?')

@dp.message_handler(lambda message: not validate_username(message), state=Registration.username)
async def process_incorrect_username(message: types.Message):
    return await message.reply('Username must be a string of 2 to 30 characters')

@dp.message_handler(validate_age, state=Registration.age)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    await Registration.next()
    keyboard = [ [
        types.KeyboardButton(text='Male'),
        types.KeyboardButton(text='Female'),
        types.KeyboardButton(text='Other'),
    ] ]
    markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Your sex?'
        )
    await message.answer('What is your sex?', reply_markup=markup)

@dp.message_handler(lambda message: not validate_age(message), state=Registration.age)
async def process_incorrect_age(message: types.Message):
    return await message.reply('Age must be a number between 14 and 100')

@dp.message_handler(lambda message: not validate_sex(message), state=Registration.sex)
async def process_incorrect_sex(message: types.Message):
    return await message.reply('Select the correct option [Male, Female, Other]')

@dp.message_handler(validate_sex, state=Registration.sex)
async def process_sex(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sex'] = message.text
    await state.finish()
    try:
        user_save(session, data)
    except ValueError:
        return await message.answer('User already exists')

    link_keyboard = get_keyboard_to_site()

    await message.answer('Thank you for your registration!', reply_markup=link_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)