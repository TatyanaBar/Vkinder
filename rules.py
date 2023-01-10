from vkbottle.tools.dev.mini_types.base import BaseMessageMin
from vkbottle.dispatch.rules import ABCRule


class PayloadRule(ABCRule[BaseMessageMin]):
    def __init__(self, payload):
        if isinstance(payload, dict):
            payload = [payload]
        self.payload = payload

   async def check(self, event: BaseMessageMin) -> bool:
        payload = event.get_payload_json()
        command = {'cmd': payload.get('cmd')}
        return command in self.payload
