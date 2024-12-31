from typing import Dict

from src.logger import logger


class RadixNode:
    def __init__(self, key: str = '', is_leaf = False):
        self.key = key
        self.is_leaf = is_leaf
        self.children: Dict[str, RadixNode] = {}
        self.value = {}

# class Message:
#     def __init__(self, data, timestamp = None):
#
class RedisStream:
    root: RadixNode
    last_id = '0-0'

    def __init__(self):
        self.root: RadixNode = RadixNode()

    def XADD(self, stream_key, data, id):
        current = self.root
        if id <= "0-0":
            raise Exception("The ID specified in XADD must be greater than 0-0")
        if id <= self.last_id:
            raise Exception("The ID specified in XADD is equal or smaller than the target stream top item")

        self.last_id = id

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
                        new_node = RadixNode(remaining_current_key, True)
                        new_node.value = current_value
                        current.children[remaining_current_key[0]] = new_node
                else:
                    if stream_key_idx < len(current.key):
                        remaining_current_key = current.key[stream_key_idx:]
                        current.is_leaf = None
                        current_value = current.value
                        current.value = None
                        new_node = RadixNode(remaining_current_key, True)
                        new_node.value = current_value
                        current.children[remaining_current_key[0]] = new_node

                    idx += stream_key_idx - 1

            else:
                new_node = RadixNode(stream_key[idx:], True)
                new_node.value = data
                current.children[stream_key[idx]] = new_node
                logger.log(current.children)

                break
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