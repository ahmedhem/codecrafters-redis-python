from app.decoder import Decoder
from app.encoder import Encoder
from app.events.echo import EchoEvent
from app.events.ping import PingEvent

class EventHandler:
    msg: bytes

    def __init__(self, msg: bytes):
        self.msg = msg
        pass

    def execute(self):
        event, args = Decoder(msg = self.msg).execute()
        if event == "PING":
            return PingEvent(args = args).execute()
        if event == "ECHO":
            return EchoEvent(args = args).execute()

        return "Event Not Found".encode()