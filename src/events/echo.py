from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry


@RedisCommandRegistry.register("ECHO")
class EchoEvent(Event):
    supported_actions: list = [KEYWORDS.ECHO.value]

    def execute(self):
        value = self.commands[0].args
        return [Encoder(lines=value).execute()]
