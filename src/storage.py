from datetime import datetime, timedelta
from typing import Dict, Any
import re

from src.config import Config


class Storage:
    databases: Dict[int, Dict[str, Any]] = {}
    databases_lock: Dict[int, Dict[str, bool]] = {}

    def __init__(self):
        pass

    @classmethod
    def assign_default(self):
        self.databases[Config.db_nr] = {}
        self.databases_lock[Config.db_nr] = {}

    @classmethod
    def get_keys(self, regex=".*"):
        keys = self.databases[Config.db_nr].keys()
        matched_keys = []
        for key in keys:
            mo = re.match(regex, key)
            if mo:
                matched_keys.append(key)

        return matched_keys

    @classmethod
    def set(self, key, value, expiry_ms=None):
        while self.databases_lock[Config.db_nr].get(key):
            continue

        self.databases_lock[Config.db_nr][key] = True

        expire_time = None
        if expiry_ms is not None:
            expire_time = datetime.utcnow() + timedelta(milliseconds=expiry_ms)

        self.databases[Config.db_nr][key] = {
            "value": value,
            "expire_time": expire_time,
            "type": 0,
        }

        self.databases_lock[Config.db_nr][key] = False

    @classmethod
    def get(self, key):
        if key in self.databases[Config.db_nr] and (
            not self.databases[Config.db_nr][key].get("expire_time")
            or self.databases[Config.db_nr][key].get("expire_time") >= datetime.now()
        ):
            return self.databases[Config.db_nr][key]["value"]

        return "-1"
