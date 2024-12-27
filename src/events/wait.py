from datetime import datetime
from time import sleep

from src.constants import KEYWORDS
from src.encoder import Encoder
from src.events.base import Event
from src.main import app

class WaitEvent(Event):
    supported_actions: list = [KEYWORDS.WAIT.value]

    def execute(self):
        replica_count = self.commands[0].args[0]
        timeout = int(self.commands[0].args[1])
        app.is_client_blocked = True
        time = datetime.utcnow()
        while True:
            current_time = datetime.utcnow()
            if app.success_ack_replica_count >= replica_count or (current_time - time).total_seconds() > timeout:
                app.is_client_blocked = False
                break
        replica_confirmed = app.success_ack_replica_count
        return [Encoder(lines=[f"{replica_confirmed}"], to_int =True).execute()]
