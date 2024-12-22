from typing import List


class Command:
    action: str
    args: List[str]

    def __init__(self, action: str, args: List[str]):
        self.action = action
        self.args = args
