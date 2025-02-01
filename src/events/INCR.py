from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage
from src.constants import TypeValue_MAP, KEYWORDS

@RedisCommandRegistry.register("INCR")
class INCREvent(Event):
    supported_actions: list = [KEYWORDS.INCR.value]

    def execute(self):
        key = self.commands[0].args[0]
        value = Storage().get(key)
        logger.log(value)
        if not value:
            Storage.set(key, 1, TypeValue_MAP['int'])
        elif value['type'] == 'int':
            Storage.set(key, int(value['value']) + 1, 1)

        return [Encoder(lines=[f'{Storage().get(key)['value']}'], to_int=True).execute()]
