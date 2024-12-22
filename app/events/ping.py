from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event


class PingEvent(Event):
    supported_actions: list = [KEYWORDS.PING.value]

    def execute(self):
        reply = "PONG"
        return Encoder(lines = [reply]).execute()
