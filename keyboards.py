from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback


search_keyboard = (
    Keyboard(one_time=True, inline=False)
    .add(Text('Поиск'))
    .get_json()
)


def get_scroll_keyboard(user_id, last, liked):
    callback_like = Callback('Нравится', payload={'cmd': 'like', 'user_id': user_id})
    callback_next = Callback('Дальше', payload={'cmd': 'next', 'user_id': user_id})
    url = f'https://vk.com/id{user_id}'
    callback_open_link = Callback('Посмотреть', payload={'cmd': 'open_link', 'link': url})

    scroll_keyboard = Keyboard(one_time=False, inline=True)
    if not liked:
        scroll_keyboard.add(callback_like, color=KeyboardButtonColor.NEGATIVE)
        if not last:
            scroll_keyboard.add(callback_next, color=KeyboardButtonColor.PRIMARY)
        scroll_keyboard.row()
    scroll_keyboard.add(callback_open_link)
    return scroll_keyboard.get_json()
