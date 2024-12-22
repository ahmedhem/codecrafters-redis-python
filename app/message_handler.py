from typing import List

from app.config import Config
from app.decoder import Decoder
from app.encoder import Encoder
from app.events.echo import EchoEvent
from app.events.ping import PingEvent
from app.events.set import SetEvent
from app.events.get import GetEvent
from app.events.config import ConfigEvent
from app.constants import keywords_args_len
from app.models.command import Command


class MessageHandler:
    msg: bytes

    def __init__(self, msg: bytes):
        self.msg = msg
        self.event_map = {
            "PING": PingEvent,
            "ECHO": EchoEvent,
            "SET": SetEvent,
            "GET": GetEvent,
            "CONFIG": ConfigEvent,
        }

    def format_command(self, args) -> List[Command]:
        response: List[Command] = []
        pos = 0
        while pos < len(args):
            if args[pos] not in keywords_args_len.keys():
               raise Exception(f"{args[pos]} is not a action")

            action = args[pos]
            args_len = keywords_args_len[action]
            if pos + args_len >= len(args):
                raise Exception(f"{args[pos]} needs {args_len} arguments")
            response.append(Command(action = action, args = args[pos + 1:pos + args_len + 1]))
            pos += args_len + 1
        return response


    def execute(self):
        commands = self.format_command(Decoder(msg = self.msg).execute())
        event = commands[0].action
        cls = self.event_map.get(event)

        if not cls:
            raise ValueError(f"Unknown event type: {event}")

        return cls(commands=commands).execute()
