import time
from typing import Dict

from src.logger import logger

class ID:
    timestamp: int
    sequence: int

    def __init__(self, timestamp: int, sequence: int):
        self.timestamp = timestamp
        self.sequence = sequence

    def __str__(self):
        return f"{self.timestamp}-{str(self.sequence)}"

    def generate_bigger(self, id):
        if id == '*':
            timestamp = sequence = '*'
        else:
            timestamp, sequence = id.split('-')
        ret = ''
        if timestamp != '*' and sequence != '*' :
            ret =  ID(timestamp=timestamp, sequence=sequence)
        elif timestamp != '*' :
            if timestamp == '0' :
                ret = ID(timestamp=timestamp, sequence=1)
            elif timestamp == self.timestamp:
                ret =  ID(timestamp=timestamp, sequence=self.sequence + 1)
            else:
                ret =  ID(timestamp=timestamp, sequence=0)
        elif sequence == '*'  and timestamp == '*' :
            ret = ID(timestamp=int(time.time() * 1000), sequence=0)
        if str(ret) <= "0-0":
            raise Exception("The ID specified in XADD must be greater than 0-0")
        if str(ret) <= str(self):
            raise Exception("The ID specified in XADD is equal or smaller than the target stream top item")

        return ret

class RadixNode:
    def __init__(self, key: str = '', id: ID = None, is_leaf = False):
        self.key = key
        self.is_leaf = is_leaf
        self.id = id
        self.children: Dict[str, RadixNode] = {}
        self.value = {}


class RedisStream:
    root: RadixNode
    last_id = ID

    def __init__(self):
        self.last_id = ID(0, 0)

        self.root: RadixNode = RadixNode(id=self.last_id)

    def XADD(self, stream_key, data, id):
        current = self.root

        self.last_id = self.last_id.generate_bigger(id)

        for idx in range(len(stream_key)):
            if current.children.get(stream_key[idx]) is not None:
                current = current.children[stream_key[idx]]
                stream_key_idx = 0
                for stream_idx in range(idx, len(stream_key)):
                    if stream_key_idx == len(stream_key):
                        break
                    if current.key[stream_key_idx] == stream_key[stream_idx]:
                        stream_key_idx += 1
                    else:
                        break

                if stream_key_idx == len(stream_key) - idx - 1:
                    # we reached a prefix
                    current_value = current.value
                    current_key = current.key
                    remaining_stream = stream_key[idx:]
                    current.value = data
                    current.key = remaining_stream
                    if len(current_key) > len(remaining_stream):
                        remaining_current_key = current_key[len(remaining_stream):]
                        current.is_leaf = False
                        new_node = RadixNode(remaining_current_key, self.last_id, True)
                        new_node.value = current_value
                        current.children[remaining_current_key[0]] = new_node
                else:
                    if stream_key_idx < len(current.key):
                        remaining_current_key = current.key[stream_key_idx:]
                        current.is_leaf = None
                        current_value = current.value
                        current.value = None
                        new_node = RadixNode(remaining_current_key, self.last_id, True)
                        new_node.value = current_value
                        current.children[remaining_current_key[0]] = new_node

                    idx += stream_key_idx - 1

            else:
                new_node = RadixNode(stream_key[idx:], self.last_id, True)
                new_node.value = data
                current.children[stream_key[idx]] = new_node
                logger.log(current.children)

                break

        return str(self.last_id)
    # a{abc}
    def read(self, stream_key):
        current = self.root
        idx = 0

        while idx < len(stream_key):
            if current.children.get(stream_key[idx]) is not None:
                current = current.children[stream_key[idx]]
                if current.key != stream_key[idx:idx+len(current.key)]:
                    return None
                idx += len(current.key)
            else:
                return None

        logger.log(current.value)

        return current.value

REDIS_STREAM = RedisStream()