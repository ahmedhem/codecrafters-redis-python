from typing import List


class Event:
    args: List[str]

    def __init__(self, args: List[str]):
        self.args = args


    def execute(self):
        pass