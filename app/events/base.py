from typing import List

from app.models.command import Command


class Event:
    commands: List[Command]
    supported_actions: list = []

    def __init__(self, commands: List[Command]):
        self.commands = commands
        if not self.validate_commands():
            raise Exception(f"Some commands are not supported for event {self.commands[0].action}")

    def validate_commands(self) -> bool:
        for command in self.commands:
            if command.action not in self.supported_actions:
                return False

        return True

    def execute(self):
        pass