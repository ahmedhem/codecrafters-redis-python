import asyncio
import select
import socket
import threading
from pickle import PROTO


def handle_multiple_connections_with_select(server):
    inputs = [server]
    while True:
        readable, _, _ = select.select(inputs, [], [], 1.0)
        for sock in readable:
            if sock is server:
                client_socket, client_address = sock.accept()
                print(f"Connection from {client_address}")
                inputs.append(client_socket)
            else:
                data = sock.recv(1024)
                if data:
                    reply = "+PONG\r\n"
                    for msg in data.splitlines():
                        msg = msg.decode('utf-8')
                        if msg == "PING":
                            sock.send(reply.encode('utf-8'))
                else:
                    print("Client disconnected")
                    inputs.remove(sock)
                    sock.close()

def handle_multiple_connections_with_thread(server):
    def handle_connection(sock):
        while True:
            try:
                data = sock.recv(1024)
                if data:
                    reply = "+PONG\r\n"
                    for msg in data.splitlines():
                        msg = msg.decode('utf-8')
                        if msg == "PING":
                            sock.send(reply.encode('utf-8'))
                else:
                    print("Client disconnected")
                    sock.close()
            except Exception as e:
                break

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_connection, args=(client_socket,)).start()


class ASYNCServer:
    def __init__(self):
        pass

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

            reply = "+PONG\r\n"
            for msg in data.splitlines():
                msg = msg.decode('utf-8')
                if msg == "PING":
                    writer.write(reply.encode("utf-8"))
            await writer.drain()
        writer.close()
        await writer.wait_closed()
        print("Connection Closed")
def create_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('localhost', 6379))

    server.listen(5)

    print("Server is listening on localhost:6379")

    handle_multiple_connections_with_thread(server)

def create_async_server():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ASYNCServer().start())

if __name__ == "__main__":
    # create_socket_server()
    create_async_server()