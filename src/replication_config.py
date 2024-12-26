import os
from http.client import responses

from src.client import communicate_with_server
from src.config import Config
from src.encoder import Encoder
from src.rdb_parser import RDBParser


class ReplicationConfig:
    role = "master"
    master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    master_repl_offset = "0"
    replicas_config: set = set()
    replicas_config_pending: set = set()

    def __init__(self):
        pass

    def get_attr(self):
        return [f"role:{self.role}", f'master_replid:{self.master_replid}', f'master_repl_offset:{self.master_repl_offset}']
    def start_replication(self):
        from src.main import app
        self.role = "slave"
        messages = [
            Encoder(lines=["PING"], to_array=True).execute(),
            Encoder(
                lines=f"REPLCONF listening-port {Config.port}".split(" "), to_array=True
            ).execute(),
            Encoder(lines="REPLCONF capa psync2".split(" "), to_array=True).execute(),
            Encoder(lines="PSYNC ? -1".split(" "), to_array=True).execute(),
        ]

        responses = app.send_msg(Config.master_host, Config.master_port, messages)
        RDBParser(file = responses[-1]).parse()

    @classmethod
    def add_replica_config(cls, port):
        cls.replicas_config.add(('127.0.0.1', port))
        cls.replicas_config_pending.add(('127.0.0.1', port))

    @classmethod
    def start_rdb_sync(cls):
        from src.main import app
        with open(os.path.join(Config.dir, Config.dbfilename), 'rb') as file:
            data = file.read()
        rfb_file_msg = f"${len(data)}\r\n".encode('utf-8')
        for host, port in cls.replicas_config_pending:
            app.send_msg(host, port, [rfb_file_msg, data])

replication_config = ReplicationConfig()
