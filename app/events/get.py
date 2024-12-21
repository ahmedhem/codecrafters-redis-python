from app.encoder import Encoder
from app.events.event import Event
from app.storage import Database

class GetEvent(Event):

    def execute(self):
        value = Database.get(self.args[0])
        return Encoder(lines = [value]).execute()