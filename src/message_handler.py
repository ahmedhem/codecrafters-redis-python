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
from src.logger import logger


class MessageHandler:
    msg: bytes
    buffered_msg = []

    def __init__(self, msg: bytes = None, buffered_msg=None):
        self.msg = msg
        self.buffered_msg = buffered_msg
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

    def format_command(self, commands_decoded) -> List[Command]:
        response: List[Command] = []
        logger.log("Formatting Started")
        for args in commands_decoded:
            pos = 0
            while pos < len(args):
                if args[pos] not in [key.value for key in KEYWORDS]:
                    logger.log(f"{args[pos]} is not a action")

                action_args_count = 0
                while (
                    pos + action_args_count + 1 < len(args)
                    and args[pos + action_args_count + 1]
                    not in keywords_args_len.keys()
                ):
                    action_args_count += 1

                action = args[pos]
                if action_args_count > keywords_args_len[action]:
                    logger.log(
                        f"action {action} only take {keywords_args_len[action]} arguments but {action_args_count} given {args} {self.msg}"
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
        logger.log("Formatting Ended")

        return response

    def execute(self):
        try:
            commands = self.format_command(Decoder(msg=self.msg).execute())
            responses = []
            can_replicate = False
            for command in commands:
                logger.log(f"SETSET COMMANDS: f{self.msg}")

                event = command.action
                logger.log(event)
                logger.log(command.args)
                cls = self.event_map.get(event)
                if not cls:
                    raise ValueError(f"Unknown event type: {event}")
                logger.log(command.action)
                can_replicate |= command.action == "SET"
                response_msg = cls(commands=[command]).execute()
                logger.log(response_msg)
                responses.extend(response_msg)
                replication_config.master_repl_offset += len(self.msg)

            return responses, can_replicate
        except Exception as e:
            logger.log(f"Exception in message handling: {e}"),
