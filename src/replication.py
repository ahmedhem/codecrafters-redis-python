from src.client import send_msg
from src.config import Config
from src.encoder import Encoder


class Replication:
    role = "master"
    master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    master_repl_offset = "0"

    def __init__(self, role=None, master_replid=None, master_repl_offset=None):
        self.role = role or self.role
        self.master_replid = master_replid or self.master_replid
        self.master_repl_offset = master_repl_offset or self.master_repl_offset

    @classmethod
    def start_replication(cls):
        cls.role = "slave"
        messages = [
            Encoder(lines=["PING"], to_array=True).execute(),
            Encoder(
                lines=f"REPLCONF listening-port {Config.port}".split(" "), to_array=True
            ).execute(),
            Encoder(lines="REPLCONF capa psync2".split(" "), to_array=True).execute(),
        ]

        send_msg(Config.master_host, Config.master_port, messages)
