from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event


class REPLCONFEvent(Event):
    supported_actions: list = [KEYWORDS.REPLCONF.value]
    allowed_conf = ["listening-port", "capa"]

    def execute(self):
        if len(self.commands[0].args) % 2  == 1:
            raise Exception("Not enough arguments")

        conf_key = self.commands[0].args[0]
        conf_value = self.commands[0].args[1]
        print(conf_key, conf_value)
        return Encoder(lines=["OK"]).execute()
