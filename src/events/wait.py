from datetime import datetime
from time import sleep

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.logger import logger


class WaitEvent(Event):
    supported_actions: list = [KEYWORDS.WAIT.value]

    def execute(self):
        logger.log(self.app)
        replica_count = int(self.commands[0].args[0])
        timeout = int(self.commands[0].args[1])
        self.app.is_client_blocked = True
        time = datetime.utcnow()
        logger.log(replica_count)
        logger.log(timeout)
        while True:
            current_time = datetime.utcnow()

            if self.app.success_ack_replica_count >= replica_count or (current_time - time).total_seconds() > timeout / 1000:
                logger.log(f"succeded {self.app.success_ack_replica_count}")

                self.app.is_client_blocked = False
                break

        replica_confirmed = self.app.success_ack_replica_count
        return [Encoder(lines=[f"{replica_confirmed}"], to_int =True).execute()]
