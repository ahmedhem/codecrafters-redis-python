import asyncio
from app.message_handler import MessageHandler

class ASYNCServer:
    def __init__(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start())

    async def start(self):
        server = await asyncio.start_server(self.handle_connection, host ='127.0.0.1', port = 6379)
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

