from app.encoder import Encoder
from app.events.base import Event
from app.storage import Storage
from app.constants import KEYWORDS

# TODO assume there are many actions with that are shared with another events


class SetEvent(Event):
    key: str = None
    value: str = None
    expiry_time: int = None
    supported_actions: list = [KEYWORDS.SET.value, KEYWORDS.PX.value]

    def execute(self):
        self.key = self.commands[0].args[0]
        self.value = self.commands[0].args[1]

        for command in self.commands:
            if command.action == KEYWORDS.PX.value:
                if not command.args[0].isdigit():
                    raise ValueError("Expiry time must be an integer")
                self.expiry_time = int(command.args[0])

        Storage.set(self.key, self.value, self.expiry_time)
        return Encoder(lines=["OK"]).execute()
