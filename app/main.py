import select
import socket
import threading


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


def create_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('localhost', 6379))

    server.listen(5)

    print("Server is listening on localhost:6379")

    handle_multiple_connections_with_thread(server)


if __name__ == "__main__":
    create_socket_server()