import argparse
import socket
import select
import threading
from typing import List, Optional
import time

from src.message_handler import MessageHandler
from src.config import Config
from src.rdb_parser import RDBParser
from src.replication_config import replication_config


class SocketServer:
    def __init__(self):
        self.client_host = None
        self.client_port = None
        self.server_socket = None
        self.running = False
        self.handle_server_args()
        self.client_sockets = []

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Redis file processor")
        parser.add_argument("--dir", required=False, help="Directory path")
        parser.add_argument("--dbfilename", required=False, help="dbfilename")
        parser.add_argument("--port", required=False, help="port")
        parser.add_argument("--replicaof", required=False, help="replicaof")
        return parser.parse_args()

    def handle_server_args(self):
        args = self.parse_arguments()
        if args.dir:
            Config.set_directory(args.dir)
        if args.dbfilename:
            Config.set_dbfilename(args.dbfilename)
        if args.port:
            Config.set_port(args.port)
        if args.replicaof:
            host, port = args.replicaof.split(" ")
            Config.set_master_replica(host, port)

    def start_server(self):
        """Start the server in a new thread"""
        self.run_server()

    def run_server(self):
        """Run the server main loop"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', Config.port))
        self.server_socket.listen(5)
        self.running = True
        if Config.is_replica:
            replication_config.start_replication()
        RDBParser().parse()

        print(f"Server started on port {Config.port}")

        while self.running:
            try:
                readable, _, _ = select.select([self.server_socket], [], [], 1.0)

                if self.server_socket in readable:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_connection,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

            except Exception as e:
                print(f"Server error: {e}")
                if not self.running:
                    break

    def handle_propagation(self, client_socket, event, data):
        if event == "PSYNC" and client_socket not in self.client_sockets:
            self.client_sockets.append(client_socket)

        if not Config.is_replica and event == "SET":
            print("Brodcasting....", len(self.client_sockets))
            for client in self.client_sockets:
                client.send(data)

    def handle_connection(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connections"""
        Config.client_host, Config.client_port = address
        print(f"Connection from {address}")

        # client_socket.settimeout(1.0)  # Set timeout for reads

        try:
            while self.running:
                try:
                    data = self._recv_with_timeout(client_socket, 1024)
                    if not data:
                        break
                    print(f"Received: {data}")
                    responses = MessageHandler(msg=data).execute()

                    if responses:
                        for response,event in responses:
                            client_socket.sendall(response)
                            self.handle_propagation(client_socket, event, data)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error handling client {address}: {e}")
                    break

        finally:
            # client_socket.close()
            Config.client_host = None
            Config.client_port = None
            print(f"Connection closed for {address}")

    @staticmethod
    def _recv_with_timeout(sock: socket.socket, bufsize: int, timeout: float = 1) -> Optional[bytes]:
        """Receive data with timeout"""
        ready = select.select([sock], [], [], timeout)
        if len(ready) > 0 and ready[0]:
            return sock.recv(bufsize)
        return None

    @staticmethod
    def send_msg(host: str, port: int, messages: List[bytes], timeout: float = 5) -> List[bytes]:
        """Send messages to a server and receive responses"""
        responses = []

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                s.setblocking(True)  # Make sure socket is blocking

                for msg in messages:
                    # Send message
                    total_sent = 0
                    while total_sent < len(msg):
                        sent = s.send(msg[total_sent:])
                        if sent == 0:
                            raise RuntimeError("Socket connection broken")
                        total_sent += sent

                    # Receive response
                    response_chunks = []
                    start_time = time.time()

                    while time.time() - start_time < timeout:
                        ready = select.select([s], [], [], timeout)
                        if ready[0]:
                            chunk = s.recv(1024)
                            if not chunk:  # Connection closed by server
                                break
                            print(f"Received chunk: {chunk}")
                            response_chunks.append(chunk)

                            # Check if there's more data immediately available
                            try:
                                ready = select.select([s], [], [], 0.1)
                                if not ready[0]:  # No more data available right now
                                    break
                            except select.error:
                                break
                        else:
                            if response_chunks:  # We got some data but now timed out
                                break
                            else:  # No data at all
                                print(f"No response received from {host}:{port}")
                                break

                    if response_chunks:
                        responses.append(b''.join(response_chunks))

        except Exception as e:
            print(f"Error communicating with {host}:{port}: {e}")
            raise

        return responses
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()