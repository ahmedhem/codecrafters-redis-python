from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.replication import Replication


class PSYNCEvent(Event):
    supported_actions: list = [KEYWORDS.PSYNC.value]

    def execute(self):
        return Encoder(
            lines=f"FULLRESYNC {Replication.master_replid} {Replication.master_repl_offset}".split(),
            to_simple_string=True,
        ).execute()
