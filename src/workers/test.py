import os
import threading
import time

from src.client import communicate_with_server
from src.config import Config
from src.replication_config import replication_config


def task1():
    while True:
        with open(os.path.join(Config.dir, Config.dbfilename), "rb") as file:
            data = file.read()
        rfb_file_msg = f"${len(data)}\r\n".encode("utf-8")
        for host, port in replication_config.replicas_config_pending:
            communicate_with_server(host, port, [rfb_file_msg, data])
        replication_config.replicas_config_pending.clear()
        time.sleep(5)
