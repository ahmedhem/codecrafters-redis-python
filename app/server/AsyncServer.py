import argparse
import asyncio
from app.rdb_parser import RDBParser
from app.message_handler import MessageHandler
from app.config import Config
from app.rdb_parser import RDBParser


class ASYNCServer:
    def __init__(self):
        self.handle_server_args()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start())

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Redis file processor')
        parser.add_argument('--dir', required=False, help='Directory path')
        parser.add_argument('--dbfilename', required=False, help='Database filename')

        return parser.parse_args()

    def handle_server_args(self):
        args = self.parse_arguments()
        dir = args.dir
        dbfilename = args.dbfilename
        Config.set_directory(dir)
        Config.set_dbfilename(dbfilename)

    async def start(self):
        server = await asyncio.start_server(self.handle_connection, host ='127.0.0.1', port = 6379)
        RDBParser().parse()
        async with server:
            await server.serve_forever()

    @classmethod
    async def handle_connection(cls,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter):

        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"Connection from {writer.transport.get_extra_info('peername')}")

            response = MessageHandler(msg = data).execute()
            if response:
                writer.write(response)
                await writer.drain()

        writer.close()
        await writer.wait_closed()
        print("Connection Closed")

