from  aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio


api = ''
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_ = KeyboardButton(text = 'Рассчитать')
button2_ = KeyboardButton(text = 'Информация')
kb.row(button_, button2_)

kb2 = InlineKeyboardMarkup(resize_keyboard = True)
button = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data= 'calories')
button2 = InlineKeyboardButton(text = 'Формулы расчёта', callback_data= 'formulas')
kb2.row(button, button2)


class UserState(StatesGroup):  #собираем данные
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands= ['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup = kb )


@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выбери опцию:', reply_markup = kb2)


@dp.callback_query_handler(text= 'formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введи свой возраст:')
    await UserState.age.set()   #запись возраста


@dp.message_handler()
async def all_message(message):
    await message.answer('Введи команду /start, чтобы начать общение.')


@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    try:
        await state.update_data(age = float(message.text))
    except:
        await message.answer('Введи число, свой возраст')
        return set_age()
    await message.answer('Введи свой рост в см:')
    await UserState.growth.set()


@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    try:
        await state.update_data(growth = float(message.text))
    except:
        await message.answer('Введи число, свой рост')
        return set_growth()
    await message.answer('Введи свой вес:')
    await UserState.weight.set()


@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight =float(message.text))
    except:
        await message.answer('Введи число, свой вес')
        return send_calories()
    data = await state.get_data()
    calories = (10 * data['weight'] + 6.25 * data['growth'] -
                5 * data['age'] - 161)
    await message.answer(f'Твоя норма калорий {calories}/сутки')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates= True)


