from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger

@RedisCommandRegistry.register("REPLCONF")
class REPLCONFEvent(Event):
    supported_actions: list = [KEYWORDS.REPLCONF.value]
    allowed_conf = ["listening-port", "capa", "GETACK", "ACK"]

    def execute(self):
        conf_key = self.commands[0].args[0]
        if conf_key not in self.allowed_conf:
            raise Exception(f"{conf_key} is not a valid keyword for config")

        config_value = self.commands[0].args[1] if len(self.commands[0].args) > 1 else None
        if conf_key == "ACK":
            self.app.replicas_offset[self.app.client_socket] = int(config_value)
            logger.log(f"Replica offset {len(self.app.replicas_offset)}")
            return [Encoder(lines=[]).execute()]
        if conf_key == "GETACK":
            return [Encoder(lines=f"REPLCONF ACK {self.app.master_repl_offset}".split(), to_array=True).execute()]
        else:
            return [Encoder(lines=["OK"]).execute()]
