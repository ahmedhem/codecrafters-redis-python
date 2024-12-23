from app.rdb_parser import RDBParser
from app.server.AsyncServer import ASYNCServer

parser = RDBParser()
if __name__ == "__main__":
    parser.parse()
    ASYNCServer().start()