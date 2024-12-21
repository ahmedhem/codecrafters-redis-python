from app.decoder import Decoder
from app.encoder import Encoder
from app.events.echo import EchoEvent
from app.events.ping import PingEvent
from app.events.set import SetEvent
from app.events.get import GetEvent

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
        if event == "SET":
            return SetEvent(args = args).execute()
        if event == "GET":
            return GetEvent(args = args).execute()

        return "$-1\r\n".encode()