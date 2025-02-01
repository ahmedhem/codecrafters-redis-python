import math
from datetime import datetime
from time import sleep

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.redis_stream import REDIS_STREAM


@RedisCommandRegistry.register("XREAD")
class XREADEvent(Event):
    supported_actions: list = [KEYWORDS.XREAD.value]

    def read_streams(self, streams, times):
        # Fetch data for each stream within the specified time range
        result = []
        for idx, stream_key in enumerate(streams):
            start_time = '0-0' if times[0] == '$' else times[idx]
            end_time = f'{"9" * 18}-0'  # A very large number to represent the end of the stream
            stream_data = REDIS_STREAM.XRANGE(stream_key, start_time, end_time)
            result.append((stream_key, stream_data if stream_data else {}))
        return result

    def execute(self):
        logger.log(f"Current time:")

        next_index = 0 if not str(self.commands[0].args[0]) == 'block' else 2
        # Split the remaining arguments into streams and times
        args_length = len(self.commands[0].args)
        mid_point = next_index + 1 + (args_length - next_index) // 2

        streams = self.commands[0].args[next_index + 1: mid_point]
        times = self.commands[0].args[mid_point: args_length]
        old_result = self.read_streams(streams, times)
        logger.log(old_result)

        # Check if the first argument is 'block' to handle timeout logic
        if str(self.commands[0].args[0]) == 'block':
            start_datetime = datetime.utcnow()
            timeout_ms = int(self.commands[0].args[1])

            # Wait until the timeout period has elapsed
            if timeout_ms == 0:
                while True:
                   current = self.read_streams(streams, times)
                   if current != old_result:
                        break
            else:
                sleep(timeout_ms/1000)

        updated_result = self.read_streams(streams, times)
        new_result = []
        logger.log(updated_result)

        for idx, (stream_key, stream_data) in enumerate(updated_result):
            old_stream_data = old_result[idx][1]

            new_data = {}
            for key, values in stream_data.items():
                for value in values:
                    if not str(self.commands[0].args[0]) == 'block' or not old_stream_data.get(key) or value not in old_stream_data.get(key):
                        if not new_data.get(key):
                            new_data[key] = []
                        new_data[key].append(value)
            if new_data:
                new_result.append((stream_key, new_data))

        logger.log(new_result)
        # Process the fetched data and build the response
        response = []
        for stream_key, stream_values in new_result:
            stream_response = [stream_key]
            if not stream_values:
                continue
            for timestamp, entries in stream_values.items():
                entry_data = [[timestamp]]
                values = []

                for entry in entries:
                    for key, value in entry.items():
                        values.extend([key, value])

                entry_data[0].append(values)
                stream_response.append(entry_data)

            response.append(stream_response)

        # Encode the response and return
        if not response:
            response = ["-1"]
        return [Encoder(lines=response, to_array=True).execute()]
