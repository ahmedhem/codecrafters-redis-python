from http.client import responses
from select import select
from typing import List

from src.config import Config
from src.decoder import Decoder
from src.encoder import Encoder
from src.events.echo import EchoEvent
from src.events.fullresync import FULLRESYNC
from src.events.keys import KeysEvent
from src.events.ping import PingEvent
from src.events.set import SetEvent
from src.events.get import GetEvent
from src.events.info import INFOEvent
from src.events.psync import PSYNCEvent
from src.events.replconf import REPLCONFEvent
from src.events.config import ConfigEvent
from src.constants import keywords_args_len, KEYWORDS
from src.models.command import Command
from src.replication_config import replication_config


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
            "KEYS": KeysEvent,
            "INFO": INFOEvent,
            "REPLCONF": REPLCONFEvent,
            "PSYNC": PSYNCEvent,
            "FULLRESYNC": FULLRESYNC,
        }

    def format_command(self, args) -> List[Command]:
        response: List[Command] = []
        pos = 0

        while pos < len(args):
            if args[pos] not in [key.value for key in KEYWORDS]:
                raise Exception(f"{args[pos]} is not a action")

            action_args_count = 0
            while (
                pos + action_args_count + 1 < len(args)
                and args[pos + action_args_count + 1] not in keywords_args_len.keys()
            ):
                action_args_count += 1

            action = args[pos]
            if action_args_count > keywords_args_len[action]:
                raise Exception(
                    f"action {action} only take {keywords_args_len} arguments"
                )

            response.append(
                Command(
                    action=action,
                    args=(
                        args[pos + 1 : pos + action_args_count + 1]
                        if action_args_count > 0
                        else []
                    ),
                )
            )
            pos = pos + action_args_count + 1

        return response

    def propagate(self):
        from src.main import app
        for host, port in replication_config.replicas_config_pending:
            print("HOST AND PORT IS ", host, port)
            app.send_msg(host, port, [self.msg])

    def execute(self):
        try:
            commands = self.format_command(Decoder(msg=self.msg).execute())
            event = commands[0].action
            cls = self.event_map.get(event)

            if not cls:
                raise ValueError(f"Unknown event type: {event}")
            response = cls(commands=commands).execute()
            from src.main import app
            return response, event
        except Exception as e:
            print("Exception in message handling: ", e),