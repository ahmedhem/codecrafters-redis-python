from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event


class PingEvent(Event):
    supported_actions: list = [KEYWORDS.PING.value]

    def execute(self):
        reply = "PONG"
        return Encoder(lines=[reply]).execute()