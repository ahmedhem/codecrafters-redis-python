from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.storage import Storage
from src.constants import Types, KEYWORDS

@RedisCommandRegistry.register("DISCARD")
class DISCARDEvent(Event):
    supported_actions: list = [KEYWORDS.DISCARD.value]

    def execute(self):
        if not self.app.is_transaction.get(self.app.client_socket):
            raise Exception('DISCARD without MULTI')
        self.app.is_transaction[self.app.client_socket] = False
        self.app.msg_queue[self.app.client_socket].clear()
        return [Encoder(lines=['OK']).execute()]
