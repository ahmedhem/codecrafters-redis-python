from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.redis_stream import REDIS_STREAM


@RedisCommandRegistry.register("xrange")
class XRANGEEvent(Event):
    supported_actions: list = [KEYWORDS.XRANGE.value]

    def execute(self):

        stream_key = str(self.commands[0].args[0])
        start = self.commands[0].args[1]
        end = self.commands[0].args[2]

        if start == '-':
            start = '0-0'

        result = REDIS_STREAM.XRANGE(stream_key, start, end)
        res = []
        for time, entries in result.items():
            cur = [time]
            values = []
            for entry in entries:
                for key, value in entry.items():
                    values.append(key)
                    values.append(value)
            cur.append(values)
            res.append(cur)

        return [Encoder(lines=res, to_array=True).execute()]
