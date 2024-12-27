from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.logger import logger
from src.replication_config import replication_config


class REPLCONFEvent(Event):
    supported_actions: list = [KEYWORDS.REPLCONF.value]
    allowed_conf = ["listening-port", "capa", "GETACK"]

    def execute(self):
        conf_key = self.commands[0].args[0]
        if conf_key not in self.allowed_conf:
            raise Exception(f"{conf_key} is not a valid keyword for config")

        if conf_key == "listening-port":
            conf_value = self.commands[0].args[1]
            replication_config.add_replica_config(port=int(conf_value))

        logger.log(f"WE ARE HERE {self.commands[0].args}")

        if conf_key == "GETACK":
            return [Encoder(lines=f"REPLCONF ACK {replication_config.master_repl_offset}".split(), to_array=True).execute()]
        else:
            return [Encoder(lines=["OK"]).execute()]
