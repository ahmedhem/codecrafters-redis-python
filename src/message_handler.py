from typing import List, Tuple

from src.constants import ServerState
from src.decoder import Decoder
from src.encoder import Encoder
from src.events.base import RedisCommandRegistry
from src.logger import logger
from src.models.command import Command


class MessageHandler:
    """Handles processing and execution of Redis protocol messages."""

    def __init__(self, msg: bytes = None, buffered_msg=None, is_from_master=False, app=None):
        self.msg = msg
        self.buffered_msg = buffered_msg or []
        self.is_from_master = is_from_master
        self.app = app

        self.returnable_commands = {"REPLCONF", "GET", "INFO"}
        self.transactional_commands = {"SET", "INCR"}
        self.replica_restricted_commands = {"SET"}

    def format_command(self, decoded_commands: List[List[str]]) -> List[Command]:
        """Formats decoded messages into Command objects."""
        formatted_commands = []

        for args in decoded_commands:
            pos = 0
            while pos < len(args):
                # Find number of arguments for current command
                action_args_count = 0
                while pos + action_args_count + 1 < len(args) and not RedisCommandRegistry.get_handler(args[pos + action_args_count + 1]):
                    action_args_count += 1

                action = args[pos]
                command_args = (args[pos + 1:pos + action_args_count + 1]
                                if action_args_count > 0 else [])

                formatted_commands.append(Command(action=action, args=command_args))
                pos += action_args_count + 1

        return formatted_commands

    def execute(self) -> Tuple[List[bytes], bytes]:
        """Executes the received Redis commands and returns responses."""
        try:
            logger.log(self.msg)
            decoder = Decoder(msg=self.msg)
            split_messages = decoder.split_messages()

            commands = self.format_command(decoder.execute())

            responses = []
            to_replicate = b""

            for idx, command in enumerate(commands):
                # Get appropriate event handler
                event_handler = RedisCommandRegistry.get_handler(command.action)
                if not event_handler:
                    raise ValueError(f"Unknown command: {command.action}")

                # Check if command can be replicated
                can_replicate = (command.action == "SET" and # ADD INCR as well
                                 self.app.state == ServerState.MASTER)

                # logger.log(f"client trans {self.app.is_transaction}")
                if self.app.is_transaction.get(self.app.client_socket) and command.action and self.app.state == ServerState.MASTER and command.action != "EXEC":
                    self.app.msg_queue.append(split_messages[idx])
                    responses.append(Encoder(lines=["QUEUED"]).execute())
                    continue
                # Execute command
                response = event_handler(app=self.app, commands=[command]).execute()
                # Add response if appropriate
                if response and (self.app.state == ServerState.MASTER or command.action in self.returnable_commands):
                    responses.extend(response)

                # Handle replication logic
                if can_replicate:
                    to_replicate += split_messages[idx]

                # Update offsets
                if self.is_from_master or self.app.state == ServerState.REPLICA:
                    self.app.master_repl_offset += len(split_messages[idx])

                if self.app.state == ServerState.MASTER and command.action == "SET":
                    self.app.master_offset += len(split_messages[idx])

            return responses, to_replicate

        except Exception as e:
            logger.log(f"Error handling message: {str(e)}")
            raise

