import math
from datetime import datetime

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.redis_stream import REDIS_STREAM


@RedisCommandRegistry.register("XREAD")
class XREADEvent(Event):
    supported_actions: list = [KEYWORDS.XREAD.value]

    def execute(self):
        if str(self.commands[0].args[0]) == 'block':
            time = datetime.utcnow()
            timeout = int(self.commands[0].args[1])
            while True:
                current_time = datetime.utcnow()
                if (current_time - time).total_seconds() > timeout / 1000:
                    break

        streams_hardcoded_string = str(self.commands[0].args[0]) if str(self.commands[0].args[0]) != 'block' else str(self.commands[0].args[2])
        result = []
        response = []
        streams = []
        times = []
        for idx in range(1, int(len(self.commands[0].args) / 2 + 1)):
            streams.append(self.commands[0].args[idx])
        for idx in range(1 + int(len(self.commands[0].args) / 2), len(self.commands[0].args)):
            times.append(self.commands[0].args[idx])
        logger.log(streams)
        logger.log(times)
        for idx in range(len(streams)):
            stream_key = streams[idx]
            start = times[idx]
            end = f'{int(1e18)}-0'

            result.append((stream_key, REDIS_STREAM.XRANGE(stream_key, start, end)))

        for stream_key, values in result:
            logger.log(result)
            now = [stream_key]
            for time, entries in values.items():
                cur = [[time]]
                values = []
                for entry in entries:
                    for key, value in entry.items():
                        values.append(key)
                        values.append(value)
                cur[0].append(values)
                now.append(cur)
            response.append(now)
        logger.log(response)
        return [Encoder(lines=response, to_array=True).execute()]
