import os



class Config:
    dir = f"{os.getcwd()}/src/assets/"
    dbfilename = "dump.rdb"
    db_nr = 0

    def __init__(self, dir=None, dbfilename=None):
        self.dir = dir or self.dir
        self.dbfilename = dbfilename or self.dbfilename

    @classmethod
    def set_directory(cls, dir):
        cls.dir = dir

    @classmethod
    def set_dbfilename(cls, dbfilename):
        cls.dbfilename = dbfilename