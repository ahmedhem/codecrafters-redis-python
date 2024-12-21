from app.encoder import Encoder
from app.events.event import Event
from app.storage import storage

class SetEvent(Event):

    def execute(self):
        storage[self.args[0]] = self.args[1]
        return Encoder(lines = ["OK"]).execute()