import select
import threading
import socket

class SocketServer:
    server_socket = None

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', 6379))
        self.server_socket.listen(5)
        print("Server is listening on localhost:6379")
        self.handle_connections_with_thread()

    def handle_connections_with_thread(self):
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
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=handle_connection, args=(client_socket,)).start()



    def handle_connections_with_select(self):
        inputs = [self.server_socket]
        while True:
            readable, _, _ = select.select(inputs, [], [], 1.0)
            for sock in readable:
                if sock is self.server_socket:
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

