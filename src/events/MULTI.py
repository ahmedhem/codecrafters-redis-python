from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage
from src.constants import Types, KEYWORDS

@RedisCommandRegistry.register("MULTI")
class MULTIEvent(Event):
    supported_actions: list = [KEYWORDS.MULTI.value]

    def execute(self):
        return [Encoder(lines=['OK']).execute()]
