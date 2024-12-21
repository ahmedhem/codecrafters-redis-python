from app.encoder import Encoder
from app.events.event import Event


class PingEvent(Event):

    def execute(self):
        reply = "PONG"
        return Encoder(lines = [reply]).execute()
