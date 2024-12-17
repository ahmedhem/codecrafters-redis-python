import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 6379))  # Binding to localhost and port 12345
    client_socket, client_address = server.accept()
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        reply = f"PONG\r\n"
        client_socket.send(reply.encode('utf-8'))

if __name__ == "__main__":
    start_server()
