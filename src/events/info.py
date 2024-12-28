from src.constants import KEYWORDS
from src.encoder import Encoder

from src.events.base import Event, RedisCommandRegistry


@RedisCommandRegistry.register("INFO")
class INFOEvent(Event):
    supported_actions: list = [KEYWORDS.INFO.value]

    def execute(self):
        key_value_pairs = []
        value = self.commands[0].args[0]
        if value == "replication":
            key_value_pairs = [
                f"role:{self.app.state.value}",
                f"master_replid:{self.app.master_replid}",
                f"master_repl_offset:{self.app.master_repl_offset}",
            ]

        return [Encoder(lines=key_value_pairs).execute()]
