from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger


@RedisCommandRegistry.register("PING")
class PingEvent(Event):
    supported_actions: list = [KEYWORDS.PING.value]

    def execute(self):
        reply = "PONG"
        return [Encoder(lines=[reply]).execute()]
