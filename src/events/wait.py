from datetime import datetime
from time import sleep

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event, RedisCommandRegistry
from src.logger import logger


@RedisCommandRegistry.register("WAIT")
class WaitEvent(Event):
    supported_actions: list = [KEYWORDS.WAIT.value]

    def execute(self):
        logger.log(self.app)
        replica_count = int(self.commands[0].args[0])
        timeout = int(self.commands[0].args[1])
        self.app.is_client_blocked = True
        time = datetime.utcnow()

        for idx, replica_socket in enumerate(self.app.replicas):
            replica_socket[0].send(Encoder(lines="REPLCONF GETACK *".split(), to_array=True).execute())

        while True:
            current_time = datetime.utcnow()
            synced_replicas_count = 0
            for replica, offset in self.app.replicas_offset.items():
                synced_replicas_count += offset >= self.app.master_offset

            if synced_replicas_count >= replica_count or (current_time - time).total_seconds() > timeout / 1000:
                self.app.is_client_blocked = False
                break

        return [Encoder(lines=[f"{synced_replicas_count}"], to_int =True).execute()]
