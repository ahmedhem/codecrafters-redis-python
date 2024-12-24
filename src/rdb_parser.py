from __future__ import annotations

import struct
from datetime import datetime, timedelta
from typing import BinaryIO
from src.storage import Storage
import os

from src.config import Config


class RDBParser:
    def __init__(self):
        self.file_path = os.path.join(Config.dir, Config.dbfilename)
        self.file: BinaryIO | None = None
        self.version = b"0011"  # Default RDB version

    def read_length(self):
        byte = self.file.read(1)
        byte = ord(byte)
        print(byte)
        bits = byte & 0xC0
        print(bits)
        if bits == 0:
            return (byte & 0x3F), 1
        elif bits == 2:
            return (self.file.read(4)).decode(), 1
        elif bits == 1:
            extra_byte = ord(self.file.read(1))
            return (
                (byte & 0x3F) << 8
            ) | extra_byte, 1  # Combine the 6 bits from the first byte with all 8 bits of the second byte
        else:
            byte = byte & 0x3F
            print(byte)
            if byte == 0xC0:
                return 1, 0
            elif byte == 0xC1:
                return 2, 0
            elif byte == 0xC2:
                return 4, 0
            else:
                raise NotImplementedError(f"{byte} is not supported")

    def read_encoded_string(self):
        len, type = self.read_length()
        print(len)
        res = self.file.read(len)
        if type == 1:
            return res.decode()
        else:
            return res  # Special case

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
                    if op_code == b"\xfa":
                        key = self.read_encoded_string()
                        value = self.read_encoded_string()
                    elif op_code == b"\xfe":
                        database_nr = self.read_length()[0]
                    elif op_code == b"\xfb":
                        hash_table_size = self.read_length()[0]
                        expire_hash_table_size = self.read_length()[0]
                    elif op_code == b"\xff":
                        checksum = self.file.read(8)
                        break
                    else:
                        expire_datetime = None
                        if op_code == b"\xfd":
                            data = self.file.read(8)
                            expire_time = int.from_bytes(data, byteorder="little")
                            expire_datetime = datetime.fromtimestamp(expire_time)
                            value_type = self.file.read(1)
                        elif op_code == b"\xfc":
                            data = self.file.read(8)
                            expire_time = int.from_bytes(data, byteorder="little")
                            expire_datetime = datetime.fromtimestamp(expire_time / 1000)
                            value_type = self.file.read(1)
                        else:
                            value_type = op_code

                        key = self.read_encoded_string()
                        value_type = ord(value_type)
                        if value_type == 0x00:  # string
                            value = self.read_encoded_string()
                        if value_type == 1:  # list
                            value = []
                            size = self.read_length()[0]
                            for _ in range(size):
                                value.append(self.read_encoded_string())

                        if not Storage.databases.get(database_nr):
                            Storage.assign_default()

                        print(key, value)
                        Storage.databases[database_nr][key] = {
                            "value": value,
                            "type": value_type,
                            "expire_time": expire_datetime,
                        }
        except FileNotFoundError:
            print("File not found")
            if not Storage.databases.get(Config.db_nr):
                Storage.assign_default()
        except Exception as e:
            print("couldn't parse RDB file")
            raise
