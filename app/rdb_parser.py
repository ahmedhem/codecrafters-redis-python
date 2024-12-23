from __future__ import annotations

from datetime import datetime, timedelta
from typing import BinaryIO
from app.storage import Storage
import os

from app.config import Config


class RDBParser:
    def __init__(self):
        self.file_path = os.getcwd() + Config.dir + Config.dbfilename
        self.file: BinaryIO | None = None
        self.version = b"0011"  # Default RDB version

    def read_length(self):
        byte = self.file.read(1)
        byte = ord(byte)
        bits = (byte & 0xC0)
        if bits == 0:
            return (byte & 0x3F), 1
        elif bits == 2:
            return (self.file.read(4)).decode(), 1
        elif bits == 1:
            extra_byte = ord(self.file.read(1))
            return ((byte & 0x3F) << 8) | extra_byte, 1  # Combine the 6 bits from the first byte with all 8 bits of the second byte
        else:
            return 1 << (byte & 0x3F), 2


    def read_encoded_string(self):
        len, type = self.read_length()
        res = self.file.read(len)
        if type == 1:
            return res.decode()
        else:
            return res # Special case


    def parse(self):
        try:
            with open(self.file_path, "rb") as self.file:
                magic_string = self.file.read(5)
                if magic_string != b"REDIS":
                    raise Exception("Invalid magic string")
                redis_version = self.file.read(4)
                if redis_version != self.version:
                    raise Exception("Invalid redis version")
                database_nr = None
                while True:
                    op_code = self.file.read(1)
                    if op_code == b'\xfa':
                        key = self.read_encoded_string()
                        value = self.read_encoded_string()
                    elif op_code == b'\xfe':
                        database_nr = self.read_length()[0]
                    elif op_code == b'\xfb':
                        hash_table_size = self.read_length()[0]
                        expire_hash_table_size = self.read_length()[0]
                    elif op_code == b'\xff':
                        checksum = self.file.read(8)
                        break
                    else:
                        expire_time = None
                        if op_code == b'\xfd':
                            time = self.file.read(4)
                            expire_time = datetime.now() + timedelta(seconds=int.from_bytes(time, byteorder='little'))
                            value_type = self.file.read(1)
                        elif op_code == b'\xfc':
                            time = self.file.read(4)
                            expire_time = datetime.now() + timedelta(milliseconds=int.from_bytes(time, byteorder='little'))
                            value_type = self.file.read(1)
                        else:
                            value_type = op_code

                        key = self.read_encoded_string()
                        value_type = ord(value_type)
                        if value_type == 0x00: # string
                            value = self.read_encoded_string()
                        if value_type == 1: # list
                            value = []
                            size = self.read_length()[0]
                            for _ in range(size):
                                value.append(self.read_encoded_string())

                        if not Storage.databases.get(database_nr):
                            Storage.assign_default()

                        Storage.databases[database_nr][key] = {
                            'value': value,
                            'type': value_type,
                            'expire_time': expire_time,
                        }

        except FileNotFoundError:
            if not Storage.databases.get(Config.db_nr):
                Storage.assign_default()
        except Exception:
            print("couldn't parse RDB file")
            raise
