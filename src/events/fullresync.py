from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.rdb_parser import RDBParser


class FULLRESYNC(Event):
    supported_actions: list = [KEYWORDS.FULLRESYNC.value]

    def execute(self):

        rdb_file = self.commands[0].args[0]
        print("resyncing")
        return Encoder(lines=["OK"]).execute()
