class Config:
    dir = "/redis-rdb-files/"
    dbfilename = "dump.rdb"
    db_nr = 0
    port = 6379

    def __init__(self, dir = None, dbfilename = None, port = None):
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
        cls.port = port