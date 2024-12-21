from app.encoder import Encoder
from app.events.event import Event
from app.storage import storage

class GetEvent(Event):

    def execute(self):
        value = storage.get(self.args[0]) or "-1"
        return Encoder(lines = [value]).execute()