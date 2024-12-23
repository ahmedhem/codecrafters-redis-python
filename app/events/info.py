from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event
from app.info import Replication

INFO_commands_map:dict = {
    "replication": Replication()
}

class INFOEvent(Event):
    supported_actions: list = [KEYWORDS.INFO.value]
    def execute(self):
        key_value_pairs = []

        if not self.commands[0].args:
            for cls in INFO_commands_map.values():
                attributes = vars(cls)
                for key, value in attributes.items():
                    key_value_pairs.append(f"{key}:{value}")
        else:
            value = self.commands[0].args[0]
            if value not in INFO_commands_map.keys():
                raise ValueError(f"Command '{value}' is not supported")
            attributes = vars(INFO_commands_map[value])
            for key, value in attributes.items():
                key_value_pairs.append(f"{key}:{value}")

        return Encoder(lines = key_value_pairs).execute()
