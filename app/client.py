import socket


def send_message(client_socket, message_id, content):
    # Send the message with a unique ID (e.g., 'msg_1')
    message = f"{message_id}: {content}"
    client_socket.send(message.encode("utf-8"))


def receive_reply(client_socket):
    # Receive the reply from the server
    reply = client_socket.recv(1024).decode("utf-8")
    print(f"Received reply: {reply}")


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6379))  # Connecting to server on localhost, port 12345

    # Send multiple messages with different IDs
    send_message(client, "msg_1", "PING")
    receive_reply(client)

    send_message(client, "msg_2", "Another message to reply to")
    receive_reply(client)

    client.close()


if __name__ == "__main__":
    start_client()
