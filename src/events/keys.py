import re
from typing import List

from src.config import Config
from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.storage import Storage


class KeysEvent(Event):
    supported_actions = [KEYWORDS.KEYS.value]

    def execute(self):
        regex = self.commands[0].args[0]
        regex = regex.replace("*", ".*")
        result = Storage.get_keys(regex)
        return Encoder(lines=result, to_array=True).execute()
