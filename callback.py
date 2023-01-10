from vkbottle import GroupEventType, CtxStorage
from vkbottle.bot import BotLabeler, MessageEvent, Message

from base import get_user_from_db, is_viewed, add_view_in_db, add_like_in_db
from messages import not_found, end_search
from config import api
from keyboards import get_scroll_keyboard
from rules import PayloadRule
from utils import date_to_age, reversed_sex_table


ctx = CtxStorage()
callback_labeler = BotLabeler()


async def search_users(user):
    ctx_users = ctx.get('users')
    if ctx_users:
        return ctx_users

    params = {
        'offset': 0,
        'count': 1000,
        'has_photo': 1,
        'sex': reversed_sex_table[user.sex_id],
        'hometown': user.city,
        'age_from': user.age,
        'age_to': user.age,
        'status': user.relation,
        'fields': [
            'is_friend',
            'is_closed',
            'blacklisted',
            'blacklisted_by_me',
            'can_write_private_message',
            'bdate',
            'verified',
        ],
    }

    suitable_users = []
    users_object = await api.users.search(**params)
    found_users = users_object.items
    for user_in_issuance in found_users:
        if user_in_issuance.verified:
            continue
        elif user_in_issuance.is_closed:
            continue
        elif user_in_issuance.blacklisted:
            continue
        elif user_in_issuance.blacklisted_by_me:
            continue
        elif user_in_issuance.is_friend:
            continue
        elif not user_in_issuance.can_write_private_message:
            continue
        elif is_viewed(user.user_id, user_in_issuance.id):
            continue
        suitable_users.append(user_in_issuance)
    return suitable_users


async def search(message):
    user = get_user_from_db(message.from_id)
    found_users = await search_users(user)
    if not found_users:
        await message.answer(not_found)
        return

    first_user_found = found_users[0]
    if len(found_users) < 2:
        await send_user(first_user_found, message=message, last=True)
    else:
        await send_user(first_user_found, message=message)
        ctx.set('users', found_users[1:])


async def get_thumb_user_photos(user_id):
    photos_object = await api.photos.get_all(owner_id=user_id, count=3, skip_hidden=1)
    photos = photos_object.items
    return ','.join([f'photo{photo.owner_id}_{photo.id}' for photo in photos])


async def send_user(user, message, change_message=True, liked=False, last=False):
    carousel_keyboard = get_scroll_keyboard(user.id, last=last, liked=liked)
    photos = await get_thumb_user_photos(user.id)
    name = f'{user.first_name} {user.last_name}'
    age = date_to_age(user.bdate)
    text = f'{name}\nВозраст: {age}'
    if isinstance(message, Message):
        await message.answer(text=text, attachment=photos, keyboard=carousel_keyboard)
        return

    if not isinstance(message, MessageEvent):
        return

    if change_message:
        await message.edit_message(message=text, attachment=photos, keyboard=carousel_keyboard)
    else:
        await message.send_message(message=text, attachment=photos, keyboard=carousel_keyboard)


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'open_link'}))
async def open_link(event: MessageEvent):
    link = event.object.payload['link']
    await event.open_link(link)


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'next'}))
async def next_user(event: MessageEvent):
    user = get_user_from_db(event.user_id)
    found_users = await search_users(user)
    if not found_users:
        await event.send_message(end_search)
        return
    first_user_found = found_users[1]
    add_view_in_db(event.user_id, first_user_found.id)
    if len(found_users) < 2:
        await send_user(first_user_found, message=event, last=True)
        ctx.set('users', [])
        return

    await send_user(first_user_found, message=event)
    ctx.set('users', found_users[2:])


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'like'}))
async def like_user(event: MessageEvent):
    liked_user_id = event.object.payload.get('user_id')
    liked_users = await api.users.get(liked_user_id, fields=['sex', 'city', 'bdate', 'relation'])
    liked_user = liked_users[0]
    await send_user(liked_user, message=event, liked=True)
    add_like_in_db(event.user_id, liked_user_id)

    user = get_user_from_db(event.user_id)
    found_users = await search_users(user)
    if not found_users:
        await event.send_message(end_search)
        return

    first_user_found = found_users[0]
    add_view_in_db(event.user_id, first_user_found.id)
    if len(found_users) < 2:
        await send_user(liked_user, message=event, change_message=False, last=True)
        ctx.set('users', [])
        return
    await send_user(first_user_found, message=event, change_message=False)
    ctx.set('users', found_users[1:])
