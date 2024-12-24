import inspect

from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event
from app.info import Replication

INFO_commands_map: dict = {"replication": Replication}


class INFOEvent(Event):
    supported_actions: list = [KEYWORDS.INFO.value]

    def execute(self):
        key_value_pairs = []

        if not self.commands[0].args:
            for cls in INFO_commands_map.values():
                key_value_pairs.extend(
                    [
                        f"{i[0]}:{i[1]}"
                        for i in vars(cls).items()
                        if not i[0].startswith("__")
                    ]
                )
        else:
            value = self.commands[0].args[0]
            if value not in INFO_commands_map.keys():
                raise ValueError(f"Command '{value}' is not supported")
            key_value_pairs = [
                f"{i[0]}:{i[1]}"
                for i in vars(INFO_commands_map[value]).items()
                if not i[0].startswith("__")
            ]

        return Encoder(lines=key_value_pairs).execute()
