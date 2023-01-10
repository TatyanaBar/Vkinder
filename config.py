import os

from vkbottle import API, BuiltinStateDispenser


COMMUNITY_TOKEN = os.getenv('COMMUNITY_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')


api = API(USER_TOKEN)
state_dispenser = BuiltinStateDispenser()
