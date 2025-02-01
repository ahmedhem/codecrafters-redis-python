from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage
from src.constants import ValueType_MAP, KEYWORDS
# TODO assume there are many actions with that are shared with another events

@RedisCommandRegistry.register("SET")
class SetEvent(Event):
    key: str = None
    value: str = None
    expiry_time: int = None
    supported_actions: list = [KEYWORDS.SET.value]

    def get_type(self):
        if self.value is str:
            return ValueType_MAP[0]
        elif self.value is int:
            return ValueType_MAP[1]

    def get_expiry_time(self):
        for idx in range(len(self.commands[0].args) - 1):
                if self.commands[0].args[idx] == 'px' and self.commands[0].args[idx + 1].isdigit():
                    return int(self.commands[0].args[idx + 1])
        return None
    def execute(self):
        self.key = self.commands[0].args[0]
        self.value = self.commands[0].args[1]
        self.expiry_time = self.get_expiry_time()
        logger.log(f"{self.key} {self.value}{self.expiry_time}")

        Storage.set(self.key, self.value, self.get_type(), self.expiry_time)

        return [Encoder(lines=["OK"]).execute()]
