import socket


def send_msg(host, port, msgs):
    responses = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            for msg in msgs:
                s.sendall(msg)
                response = s.recv(4096)
                responses.append(response)
        return responses
    except Exception as e:
        print(f"Could not send message {msgs}")
