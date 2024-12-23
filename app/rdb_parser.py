from __future__ import annotations

import struct
from datetime import datetime, timedelta
from typing import BinaryIO
from app.storage import Storage
import os

from app.config import Config


class RDBParser:
    def __init__(self):
        self.file_path = os.path.join(Config.dir, Config.dbfilename)
        self.file: BinaryIO | None = None
        self.version = b"0011"  # Default RDB version

    def read_length(self):
        byte = ord(self.file.read(1))
        bits = byte & 0xC0  # Get first 2 bits (11000000)

        if bits == 0:  # 00xxxxxx - 6 bit number
            return byte & 0x3F, 1

        elif bits == 0x40:  # 01xxxxxx - 14 bit number
            next_byte = ord(self.file.read(1))
            return ((byte & 0x3F) << 8) | next_byte, 1

        elif bits == 0x80:  # 10xxxxxx
            # Length is in next 4 bytes
            length = struct.unpack('>I', self.file.read(4))[0]
            return length, 1

        elif byte == 0xC0:  # 11000000 - int 8
            # integer = struct.unpack('>B', self.file.read(1))[0]
            return 1, 2

        elif byte == 0xC1:  # 11000001 - int 16
            # integer = struct.unpack('>H', self.file.read(2))[0]
            return 2, 2

        elif byte == 0xC2:  # 11000010 - int 32
            # integer = struct.unpack('>I', self.file.read(4))[0]
            return 4, 2

        raise ValueError(f"Invalid length encoding byte: {byte:02x}")


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
                        expire_datetime = None
                        if op_code == b'\xfd':
                            data = self.file.read(8)
                            expire_time = int.from_bytes(data, byteorder="little")
                            expire_datetime = datetime.fromtimestamp(expire_time)
                            value_type = self.file.read(1)
                        elif op_code == b'\xfc':
                            data = self.file.read(8)
                            expire_time = int.from_bytes(data, byteorder="little")
                            expire_datetime = datetime.fromtimestamp(expire_time/1000)
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
                            'expire_time': expire_datetime,
                        }

        except FileNotFoundError:
            print("File not found")
            if not Storage.databases.get(Config.db_nr):
                Storage.assign_default()
        except Exception as e:
            print("couldn't parse RDB file")
            raise
