from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.redis_stream import REDIS_STREAM


@RedisCommandRegistry.register("XADD")
class XADDEvent(Event):
    supported_actions: list = [KEYWORDS.XADD.value]

    def execute(self):

        stream_key = None
        value = {}
        stream_key = str(self.commands[0].args[0])
        id = self.commands[0].args[1]
        for idx in range(2, len(self.commands[0].args), 2):
            value[self.commands[0].args[idx]] = self.commands[0].args[idx + 1]

        REDIS_STREAM.XADD(stream_key, value, id)

        return [Encoder(lines=[id]).execute()]
