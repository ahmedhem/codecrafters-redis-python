import math

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.redis_stream import REDIS_STREAM


@RedisCommandRegistry.register("XREAD")
class XREADEvent(Event):
    supported_actions: list = [KEYWORDS.XREAD.value]

    def execute(self):

        streams_hardcoded_string = str(self.commands[0].args[0])
        stream_key = self.commands[0].args[1]
        start = self.commands[0].args[2]
        end = f'{int(1e18)}-0'

        result = REDIS_STREAM.XRANGE(stream_key, start, end)
        res = []
        for time, entries in result.items():
            now = [stream_key]
            cur = [[time]]
            values = []
            for entry in entries:
                for key, value in entry.items():
                    values.append(key)
                    values.append(value)
            cur[0].append(values)
            now.append(cur)
            res.append(now)
        logger.log(res)
        return [Encoder(lines=res, to_array=True).execute()]
