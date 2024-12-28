from src.constants import KEYWORDS, ServerState, ValueType
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage


@RedisCommandRegistry.register("TYPE")
class TypeEvent(Event):
    supported_actions: list = [KEYWORDS.TYPE.value]

    def execute(self):
        key = self.commands[0].args[0]
        value = Storage.get(key)
        logger.log(value)
        type = value['type'] if value != "-1" else 'none'
        return [Encoder(lines=[type], to_simple_string=True).execute()]
