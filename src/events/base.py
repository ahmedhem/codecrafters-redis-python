from typing import List, Dict, Type, Callable, Optional

from src.models.command import Command


class Event:
    commands: List[Command]
    supported_actions: list = []
    app = None
    def __init__(self, commands: List[Command], app = None):
        self.commands = commands
        self.app = app
        if not self.validate_commands():
            raise Exception(
                f"Some commands are not supported for event {self.commands[0].action}"
            )

    def validate_commands(self) -> bool:
        for command in self.commands:
            if command.action not in self.supported_actions:
                return False

        return True

    def execute(self):
        pass


class RedisCommandRegistry:
    """Registry for Redis commands and their handlers."""
    _commands: Dict[str, Type[Event]] = {}

    @classmethod
    def register(cls, command_name: str) -> Callable:
        """Decorator to register Redis command handlers."""

        def decorator(event_class: Type[Event]) -> Type[Event]:
            cls._commands[command_name] = event_class
            return event_class

        return decorator

    @classmethod
    def get_handler(cls, command_name: str) -> Optional[Type[Event]]:
        """Get the handler class for a given command."""
        return cls._commands.get(command_name)
