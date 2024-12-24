from src.config import Config
from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event


class ConfigEvent(Event):
    supported_actions: list = [
        KEYWORDS.CONFIG.value,
        KEYWORDS.GET.value,
        KEYWORDS.SET.value,
    ]

    def get_config(self, key):
        config_attr = Config.__dict__
        if key not in config_attr:
            raise Exception(f"{key} is unknown")

        return Encoder(lines=[key, config_attr[key]], to_array=True).execute()

    def set_config(self, key, value):
        pass

    def execute(self):
        for command in self.commands:
            if command.action == KEYWORDS.GET.value:
                return self.get_config(command.args[0])
            if command.action == KEYWORDS.SET.value:
                return self.set_config(command.args[0], command.args[1])
