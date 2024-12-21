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
        self.event_map = {
            "PING": PingEvent,
            "ECHO": EchoEvent,
            "SET": SetEvent,
            "GET": GetEvent
        }

    def execute(self):
        event, args = Decoder(msg = self.msg).execute()
        cls = self.event_map.get(event)

        if not cls:
            raise ValueError(f"Unknown event type: {event}")

        return cls(args=args).execute()
