from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event


class WaitEvent(Event):
    supported_actions: list = [KEYWORDS.WAIT.value]

    def execute(self):
        arg1 = self.commands[0].args[0]
        arg2 = self.commands[0].args[1]
        return [Encoder(lines=["0"], to_int =True).execute()]
