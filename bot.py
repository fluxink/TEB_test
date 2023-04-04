import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils.database import init_db, get_user, save_user, User

API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class Registration(StatesGroup):
    name = State()
    username = State()
    sex = State()
    age = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await Registration.name.set()
    await message.answer(
        '''
        Hello, let's begin the registration!
        What is your name?
        ''')

@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Registration.next()
    await message.answer('What is your username?')

@dp.message_handler(state=Registration.username)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    await Registration.next()

# Validate age
def validate_age(message: types.Message) -> bool:
    try:
        age = int(message.text)
    except ValueError:
        return False
    return 0 < age < 100

@dp.message_handler(not validate_age, state=Registration.age)
async def process_age_invalid(message: types.Message):
    return await message.reply('Age must be a number between 0 and 100')

@dp.message_handler(validate_age, state=Registration.age)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    kb = [ [
        types.KeyboardButton(text='Male'),
        types.KeyboardButton(text='Female'),
        types.KeyboardButton(text='Other'),
    ] ]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Your sex?'
        )
    await message.answer('What is your sex?', reply_markup=markup)

@dp.message_handler(state=Registration.sex)
async def process_sex(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sex'] = message.text
        data['telegram_id'] = message.from_user.id
    await message.answer('Thank you for your registration!')

async def save_user_to_db(session, user_data: dict):
    user = await get_user(session, user_data['telegram_id'])
    if user:
        raise ValueError('User already exists')
    else:
        user = User(**user_data)
    await save_user(session, user)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)