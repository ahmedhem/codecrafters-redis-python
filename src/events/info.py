from src.constants import KEYWORDS
from src.encoder import Encoder

from src.events.base import Event
from src.replication_config import replication_config

INFO_commands_map: dict = {"replication": replication_config}


class INFOEvent(Event):
    supported_actions: list = [KEYWORDS.INFO.value]

    def execute(self):
        key_value_pairs = []

        if not self.commands[0].args:
            for cls in INFO_commands_map.values():
                key_value_pairs.extend(cls.get_attr())
        else:
            value = self.commands[0].args[0]
            if value not in INFO_commands_map.keys():
                raise ValueError(f"Command '{value}' is not supported")
            key_value_pairs = INFO_commands_map[value].get_attr()
        return [Encoder(lines=key_value_pairs).execute()]
