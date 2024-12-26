import os



class Config:
    dir = f"{os.getcwd()}/src/assets/"
    dbfilename = "dump.rdb"
    db_nr = 0
    port: int = 6379
    role = "master"
    master_host = None
    master_port: int = None
    client_host: str = None
    client_port: str = None
    is_replica: bool = False

    def __init__(self, dir=None, dbfilename=None, port=None):
        self.dir = dir or self.dir
        self.dbfilename = dbfilename or self.dbfilename
        self.port = port or self.port

    @classmethod
    def set_directory(cls, dir):
        cls.dir = dir

    @classmethod
    def set_dbfilename(cls, dbfilename):
        cls.dbfilename = dbfilename

    @classmethod
    def set_port(cls, port):
        cls.port = int(port)

    @classmethod
    def set_master_replica(cls, master_host, master_port):
        from src.replication_config import replication_config

        cls.master_host = master_host
        cls.master_port = int(master_port)
        cls.is_replica = True
        replication_config.role = 'slave'
