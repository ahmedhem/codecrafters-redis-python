import argparse
import asyncio

from src.replication_config import ReplicationConfig
from src.message_handler import MessageHandler
from src.config import Config
from src.rdb_parser import RDBParser


class ASYNCServer:
    def __init__(self):
        self.handle_server_args()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start())

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Redis file processor")
        parser.add_argument("--dir", required=False, help="Directory path")
        parser.add_argument("--dbfilename", required=False, help="dbfilename")
        parser.add_argument("--port", required=False, help="port")
        parser.add_argument("--replicaof", required=False, help="replicaof")

        return parser.parse_args()

    def handle_server_args(self):
        args = self.parse_arguments()
        if args.dir:
            Config.set_directory(args.dir)
        if args.dbfilename:
            Config.set_dbfilename(args.dbfilename)
        if args.port:
            Config.set_port(args.port)
        if args.replicaof:
            host, port = args.replicaof.split(" ")
            Config.set_master_replica(host, port)
            ReplicationConfig.start_replication()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_connection, host="127.0.0.1", port=Config.port
        )
        RDBParser().parse()
        async with server:
            await server.serve_forever()

    @classmethod
    async def handle_connection(
        cls, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):

        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"Connection from {writer.transport.get_extra_info('peername')}")

            responses = MessageHandler(msg=data).execute()

            if responses:
                for response in responses:
                    writer.write(response)
            await writer.drain()

        writer.close()
        await writer.wait_closed()
        print("Connection Closed")


app = ASYNCServer()
