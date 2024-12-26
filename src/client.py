import socket
import time
from typing import List, Tuple, Optional
import select


def communicate_with_server(host: str, port: int, messages: List[bytes],
                            timeout: float = 2) -> List[bytes]:
    responses = []

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.setblocking(False)  # Make socket non-blocking

            for msg in messages:
                # Send message
                s.sendall(msg)

                # Receive response with timeout
                response_chunks = []
                start_time = time.time()

                while True:
                    try:
                        ready = select.select([s], [], [], timeout)
                        if ready[0]:
                            chunk = s.recv(1024)

                            if not chunk:
                                break
                            response_chunks.append(chunk)
                        else:
                            if response_chunks:
                                break
                            else:
                                raise socket.timeout("No response received from server")

                    except BlockingIOError:
                        continue

                if response_chunks:
                    responses.append(b''.join(response_chunks))

    except socket.error as e:
        print(f"Socket error occurred: {e}")
        raise

    return responses