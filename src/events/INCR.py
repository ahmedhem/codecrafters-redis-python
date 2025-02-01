from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage
from src.constants import TypeValue_MAP, KEYWORDS
# TODO assume there are many actions with that are shared with another events

@RedisCommandRegistry.register("INCR")
class INCREvent(Event):
    supported_actions: list = [KEYWORDS.INCR.value]

    def execute(self):
        self.key = self.commands[0].args[0]
        value = Storage().get(self.key)
        if not value:
            Storage.set(self.key, TypeValue_MAP['int'], 1)
        if value['type'] == TypeValue_MAP['int']:
            Storage.set(self.key, value['value'] + 1, 1)

        return [Encoder(lines=[f'{Storage().get(self.key)}']).execute()]
