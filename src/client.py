import socket

def send_msg(host, port, msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(msg)
            response = s.recv(1024)
            return response
    except Exception as e:
        print(f"Could not send message {msg}")
        raise

