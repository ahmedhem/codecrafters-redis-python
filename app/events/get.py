from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event
from app.storage import Database

class GetEvent(Event):
    supported_actions: list = [KEYWORDS.GET.value]

    def execute(self):
        value = Database.get(self.commands[0].args[0])
        return Encoder(lines = [value]).execute()