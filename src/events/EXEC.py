from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger
from src.constants import Types, KEYWORDS, ServerState


@RedisCommandRegistry.register("EXEC")
class EXECEvent(Event):
    supported_actions: list = [KEYWORDS.EXEC.value]

    def execute(self):
        if not self.app.is_transaction.get(self.app.client_socket):
            raise Exception('EXEC without MULTI')
        self.app.is_transaction[self.app.client_socket] = False
        responses = []
        while self.app.msg_queue[self.app.client_socket]:
            responses.extend(self.app.process_command(self.app.msg_queue[self.app.client_socket][0], is_from_master=self.app.state == ServerState.MASTER))
            self.app.msg_queue[self.app.client_socket].popleft()
        return [Encoder(lines=responses, to_simple_array=True).execute()]
