from enum import Enum

keywords_args_len: {str: int} = {
    "PING": 0,
    "SET": 2,
    "GET": 1,
    "ECHO": 1,
    "px": 1,
    "CONFIG": 0,
}

class KEYWORDS(Enum):
    PING: str = "PING"
    SET: str = "SET"
    GET: str = "GET"
    ECHO: str = "ECHO"
    PX: str = "px"
    CONFIG: str = "CONFIG"