from app.encoder import Encoder
from app.events.event import Event
from app.storage import Database

# TODO assume there are many actions with that are shared with another events
# TODO use ENUMS

class SetEvent(Event):
    key: str = None
    value: str = None
    expiry_time: int = None
    supported_actions: list = ["px"]

    def extract_actions(self):
        if len(self.args) < 2:
            raise AssertionError('need at least 2 arguments')

        self.key = self.args[0]
        self.value = self.args[1]
        if len(self.args) > 2:
            if self.args[2] not in self.supported_actions: # assuming for now we only have px
                raise AssertionError(f"action {self.args[2]} is not supported")
            else:
                if len(self.args) < 4:
                    raise AssertionError(f"missing one argument")
                # TODO handle int error
                self.expiry_time = int(self.args[3])

    def execute(self):
        self.extract_actions()
        Database.set(self.key, self.value, self.expiry_time)
        return Encoder(lines = ["OK"]).execute()