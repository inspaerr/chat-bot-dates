import aiohttp
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.deep_linking import decode_payload
from main.mongo import MongoManager
from main.settings import MasterSettings

mongo = MongoManager()

bot = Bot(token=MasterSettings.BOT_TOKEN)
dp = Dispatcher(bot)

start_chat_button = types.KeyboardButton(text='Начать чат')
start_chat_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(start_chat_button)

stop_chat_button = types.KeyboardButton(text='Закончить чат')
stop_chat_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(stop_chat_button)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.message.Message):
    await message.answer(text="Привет, для того, чтобы начать общение, заполни анкету")
    await message.answer(text="Введи своё имя (никнейм, псевдоним, позывной)")
    await mongo.register_user(message.from_user.id)