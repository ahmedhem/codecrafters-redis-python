import re
from typing import List

from app.config import Config
from app.constants import KEYWORDS
from app.encoder import Encoder
from app.events.base import Event
from app.storage import Storage

class KeysEvent(Event):
    supported_actions = [KEYWORDS.KEYS.value]

    def execute(self):
        regex = self.commands[0].args[0]
        regex = regex.replace('*', '.*')
        result = Storage.get_keys(regex)
        return Encoder(lines = result, to_array=True).execute()
