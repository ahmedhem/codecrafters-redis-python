from app.encoder import Encoder
from app.events.event import Event


class EchoEvent(Event):

    def execute(self):
        return Encoder(lines = self.args).execute()
