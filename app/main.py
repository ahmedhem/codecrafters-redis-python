import socket


def create_socket_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(('localhost', 6379))

        server.listen(1)

        print("Server is listening on localhost:6379")

        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                reply = "+PONG\r\n"
                for msg in data.splitlines():
                    msg = msg.decode('utf-8')
                    if msg == "PING":
                        client_socket.send(reply.encode('utf-8'))

            except ConnectionResetError:
                print("Client disconnected")
                break

        # Close sockets
        client_socket.close()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    create_socket_server()