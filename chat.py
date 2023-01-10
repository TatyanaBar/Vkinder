from vkbottle.bot import BotLabeler
from vkbottle.bot import Message

from messages import hello, find
from keyboards import search_keyboard
from states import check_user
from config import api


chat_labeler = BotLabeler()


@chat_labeler.private_message(text=['Начать', 'начать'])
async def start(message: Message):
    users = await api.users.get(message.from_id)
    await message.answer(hello.format(users[0].first_name), keyboard=search_keyboard)


@chat_labeler.private_message(text=['Поиск'])
async def search(message: Message):
    users = await api.users.get(message.from_id)
    await message.answer(find.format(users[0].first_name))
    await check_user(message)
