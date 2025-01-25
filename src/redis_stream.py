import time
from typing import Dict, List

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
    last_id: ID

    def __init__(self):
        self.last_id = ID(0, 0)
        self.root: RadixNode = RadixNode(id=self.last_id)
    def XADD(self, stream_key, data, id='*'):
        current = self.root

        # Generate a new ID if not provided
        self.last_id = self.last_id.generate_bigger(id)

        # Traverse the radix tree to find the correct position for the new entry
        for idx in range(len(stream_key)):
            if current.children.get(stream_key[idx]) is not None:
                current = current.children[stream_key[idx]]
                stream_key_idx = 0
                for stream_idx in range(idx, len(stream_key)):
                    if stream_key_idx == len(current.key):
                        break
                    if current.key[stream_key_idx] == stream_key[stream_idx]:
                        stream_key_idx += 1
                    else:
                        break

                if stream_key_idx == len(current.key):
                    # We reached a prefix
                    idx += stream_key_idx
                else:
                    # Split the node
                    remaining_current_key = current.key[stream_key_idx:]
                    current.key = current.key[:stream_key_idx]
                    current.is_leaf = False

                    # Create a new node for the remaining part of the key
                    new_node = RadixNode(remaining_current_key, current.id, current.is_leaf)
                    new_node.value = current.value
                    new_node.children = current.children

                    # Clear the current node's children and value
                    current.children = {remaining_current_key[0]: new_node}
                    current.value = None

                    # Move to the new node
                    current = new_node
                    idx += stream_key_idx
            else:
                # Insert new node
                new_node = RadixNode(stream_key[idx:], self.last_id, True)
                new_node.value = data
                current.children[stream_key[idx]] = new_node
                break

        # If we reached the end of the stream_key, update the current node
        if idx == len(stream_key):
            current.is_leaf = True
            current.id = self.last_id
            current.value = data

        return str(self.last_id)

    def XRANGE(self, stream_key, start, end):
        # Helper function to compare IDs
        def is_id_in_range(current_id, start_id, end_id):
            return str(start_id) <= str(current_id) <= str(end_id)

        # Convert start and end IDs to ID objects
        start_id = ID(*map(int, start.split('-')))
        end_id = ID(*map(int, end.split('-')))
        # Traverse the radix tree to find the node for the stream_key
        current = self.root
        idx = 0

        while idx < len(stream_key):
            if current.children.get(stream_key[idx]) is not None:
                current = current.children[stream_key[idx]]
                if current.key != stream_key[idx:idx + len(current.key)]:
                    return []  # Stream key not found
                idx += len(current.key)
            else:
                return []  # Stream key not found

        # If the current node is not a leaf, return empty list
        if not current.is_leaf:
            return []

        # Collect entries within the specified ID range
        result: Dict[str, List] = {}

        def add_value(key, value):
            if result.get(key) is None:
                result[key] = []
            result[key].append(value)

        if is_id_in_range(current.id, start_id, end_id):
            add_value(str(current.id), current.value)

        # Traverse children to find additional entries
        def traverse(node):
            if node.is_leaf and is_id_in_range(node.id, start_id, end_id):
                add_value(str(node.id), node.value)
            for child in node.children.values():
                traverse(child)

        for child in current.children.values():
            traverse(child)

        # Sort the result by ID
        # result.sort(key=lambda x: x[0])
        logger.log(result)
        return result
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