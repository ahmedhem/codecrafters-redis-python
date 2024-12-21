from datetime import datetime, timedelta
from turtledemo.penrose import start


class Database:
    db: dict = {}
    db_expiry: dict = {}
    db_lock: dict = {}

    def __init__(self):
        pass

    @classmethod
    def set(self, key, value, expiry_ms = None):
        while self.db_lock.get(key):
            continue

        self.db_lock[key] = True

        if expiry_ms is not None:
            self.db_expiry[key] = datetime.now() + timedelta(milliseconds=expiry_ms)

        self.db[key] = value
        self.db_lock[key] = False

    @classmethod
    def get(self, key):
        if key in self.db and (not self.db_expiry.get(key) or self.db_expiry.get(key) >= datetime.now()):
            return self.db[key]

        return "-1"
