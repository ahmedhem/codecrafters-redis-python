from enum import Enum

INF = 1e9

keywords_args_len: {str: int} = {
    "PING": 0,
    "SET": 4,
    "GET": 1,
    "ECHO": 1,
    "CONFIG": 0,
    "KEYS": 1,
    "INFO": 1,
    "REPLCONF": 2,
    "PSYNC": 2,
    "FULLRESYNC": 1,
    "WAIT": 2,
    "TYPE": 1,
    "XADD": INF,
}


class KEYWORDS(Enum):
    PING: str = "PING"
    SET: str = "SET"
    GET: str = "GET"
    ECHO: str = "ECHO"
    CONFIG: str = "CONFIG"
    KEYS: str = "KEYS"
    INFO: str = "INFO"
    REPLCONF: str = "REPLCONF"
    PSYNC: str = "PSYNC"
    FULLRESYNC: str = "FULLRESYNC"
    WAIT: str = "WAIT"
    TYPE: str = "TYPE"
    XADD: str = "XADD"


class ValueType(Enum):
    string = 0
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

ValueType_MAP = {
    0: "string"
}
class ServerState(Enum):
    STANDALONE = "standalone"
    REPLICA = "slave"
    MASTER = "master"
