from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.storage import Storage


@RedisCommandRegistry.register("GET")
class GetEvent(Event):
    supported_actions: list = [KEYWORDS.GET.value]

    def execute(self):
        ret = Storage.get(self.commands[0].args[0])
        value = ret['value'] if ret != "-1" else ret
        return [Encoder(lines=[value]).execute()]
