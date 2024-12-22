from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event


class EchoEvent(Event):
    supported_actions: list = [KEYWORDS.ECHO.value]

    def execute(self):
        value = self.commands[0].args
        return Encoder(lines = value).execute()
