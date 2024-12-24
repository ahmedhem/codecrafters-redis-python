from enum import Enum

keywords_args_len: {str: int} = {
    "PING": 0,
    "SET": 2,
    "GET": 1,
    "ECHO": 1,
    "px": 1,
    "CONFIG": 0,
    "KEYS": 1,
    "INFO": 1,
    "REPLCONF": 2,
}


class KEYWORDS(Enum):
    PING: str = "PING"
    SET: str = "SET"
    GET: str = "GET"
    ECHO: str = "ECHO"
    PX: str = "px"
    CONFIG: str = "CONFIG"
    KEYS: str = "KEYS"
    INFO: str = "INFO"
    REPLCONF: str = "REPLCONF"


class ValueType(Enum):
    STRING = 0
    LIST = 1
    SET = 2
    SORTED_SET = 3
    HASH = 4
    ZIPMAP = 9
    ZIPLIST = 10
    INTSET = 11
    SORTED_SET_ZIPLIST = 12
    HASH_ZIPLIST = 13
    LIST_ZIPLIST = 14
