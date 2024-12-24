from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.replication_config import ReplicationConfig


class REPLCONFEvent(Event):
    supported_actions: list = [KEYWORDS.REPLCONF.value]
    allowed_conf = ["listening-port", "capa"]

    def execute(self):
        if len(self.commands[0].args) % 2 == 1:
            raise Exception("Not enough arguments")

        conf_key = self.commands[0].args[0]
        if conf_key not in self.allowed_conf:
            raise Exception(f"{conf_key} is not a valid keyword for config")
        conf_value = self.commands[0].args[1]

        if conf_key == "listening-port":
            ReplicationConfig.add_replica_port(int(conf_value))

        return [Encoder(lines=["OK"]).execute()]
