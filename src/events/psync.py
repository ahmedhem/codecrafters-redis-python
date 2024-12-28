import os

from src.config import Config
from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry


@RedisCommandRegistry.register("PSYNC")
class PSYNCEvent(Event):
    supported_actions: list = [KEYWORDS.PSYNC.value]

    def execute(self):
        full_resync_msg = Encoder(
            lines=f"FULLRESYNC {self.app.master_replid} {self.app.master_repl_offset}".split(),
            to_simple_string=True,
        ).execute()
        with open(os.path.join(Config.dir, Config.dbfilename), "rb") as file:
            data = file.read()
        rfb_file_msg = f"${len(data)}\r\n".encode("utf-8")
        return [full_resync_msg, rfb_file_msg, data]
