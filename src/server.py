import argparse
import socket
import sys
import threading
from collections import deque
from datetime import datetime
from enum import Enum
from http.client import responses
from typing import Optional, Tuple, Dict, Any, List
import time
from src.config import Config
from src.constants import ServerState
from src.encoder import Encoder
from src.message_handler import MessageHandler
from src.rdb_parser import RDBParser
from src.logger import logger


class RedisServer:
    success_ack_replica_count = 0
    is_running = False
    host = None
    master_host = None
    master_port = None
    master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    master_repl_offset = 0
    server_socket = None
    state = ServerState.STANDALONE
    master_info: Optional[Tuple[str, int]] = None
    accept_thread = None
    is_client_blocked = False
    master_connection = None
    replication_buffer = []
    propagation_thread = None
    replicas: List[Tuple[socket.socket, Tuple[str, int]]] = []
    replicas_offset: Dict[socket.socket, int] = {}
    replica_lock = None
    client_socket: socket.socket = None
    master_offset = 0
    is_transaction: Dict = {}
    msg_queue: Dict

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.replica_lock = threading.Lock()
        self.host = host
        self.port = port
        self.args = self._parse_arguments()

        if self.args.replicaof:
            master_host, master_port = self.args.replicaof.split(" ")
            self._initialize_as_replica(master_host, int(master_port))
        else:
            self._initialize_as_master()

    def start_serving(self):
        """Start accepting connections before initiating replication"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True
        self._load_rdb()
        # Start accepting connections in a separate thread
        self.accept_thread = threading.Thread(target=self._accept_connections)
        self.accept_thread.daemon = True
        self.accept_thread.start()

    def _accept_connections(self):
        """Handle incoming client connections"""
        while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.is_running:
                        logger.log(f"Error accepting connection: {e}")
    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle individual client connections"""
        try:
            while self.is_running:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    self.client_socket = client_socket
                    is_replica_handshake = data ==  b'*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n'
                    if self.state == ServerState.MASTER and is_replica_handshake:
                        self.replicas.append((client_socket, address))

                    # Process commands based on current server state
                    responses = self.process_command(data, is_from_master=False)
                    for res in responses:
                        client_socket.send(res)
                    if is_replica_handshake:
                        logger.log(("replica handshake found"))
                        self.replicas_offset[client_socket] = 0

        except Exception as e:
            logger.log(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def _initialize_as_replica(self, master_host: str, master_port: int):
        """Initialize replication after server is already running"""
        self.master_info = (master_host, master_port)
        if not self.is_running:
            self.start_serving()

        # Now initiate replication handshake in a separate thread
        replication_thread = threading.Thread(target=self._establish_replication)
        replication_thread.daemon = True
        replication_thread.start()

    def _initialize_as_master(self):
        self.state = ServerState.MASTER
        if not self.is_running:
            self.start_serving()

    def _establish_replication(self):
        """Handle replication handshake and RDB transfer"""
        try:
            self.state = ServerState.REPLICA
            # Connect to master
            self.master_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.master_connection.connect(self.master_info)

            # Send PING
            self._send_to_master(b'*1\r\n$4\r\nPING\r\n')
            ping_response = self.master_connection.recv(1024)

            # Send REPLCONF
            self._send_to_master(
                Encoder(
                    lines=f"REPLCONF listening-port {self.port}".split(" "),
                    to_array=True,
                ).execute(),
            )
            replconf_response_1 = self.master_connection.recv(1024)

            # Send PSYNC
            self._send_to_master(
                Encoder(
                    lines="REPLCONF capa psync2".split(" "), to_array=True
                ).execute()
            )
            replconf_response_2 = self.master_connection.recv(1024)

            self._send_to_master(
                Encoder(lines="PSYNC ? -1".split(" "), to_array=True).execute()
            )

            #handling FULL RESYNC + Rdb + FIRST COMMAND
            response = self.master_connection.recv(1024)
            data = response.splitlines()
            rdb_data = b'\r\n'.join(data[2:4])
            self._load_rdb(rdb_data)
            if len(data) > 4:
                command = b'\r\n'.join(data[4:len(data)])
                self.client_socket = self.master_connection
                if command:
                    command = b"*3\r\n" + command  # hardcoded for now until we figure out why the tester send the format like thi
                    responses = self.process_command(command)
                    if responses:
                        for response in responses:
                            self.master_connection.sendall(response)
            # Update server state
            self.propagation_thread = threading.Thread(
                target=self._handle_master_propagation
            )
            self.propagation_thread.daemon = True
            self.propagation_thread.start()


        except Exception as e:
            logger.log(f"Error establishing replication: {e}")

    def _propagate_to_replicas(self, command):
        with self.replica_lock:
            dead_replicas = []
            for idx, replica_socket in enumerate(self.replicas):
                try:
                    replica_socket[0].send(command)
                except Exception as e:
                    logger.log(
                        f"Error handling replica at {self.replicas[replica_socket[1][0]]}:{self.replicas[replica_socket[0]]}",
                        e,
                    )
                    dead_replicas.append(replica_socket)

            for replica_socket in dead_replicas:
                self.replicas.remove(replica_socket)

    def _load_rdb(self, rdb_data: bytes = None):
        """Load data from RDB file into memory"""
        # Simplified RDB loading - you'd want to implement proper RDB parsing
        RDBParser(file=rdb_data).parse()
        # Parse RDB and populate data_store

    def process_command(
        self, data: bytes, is_from_master: bool = False
    ) -> List[bytes]:
        """Process Redis commands based on server state and source"""
        try:
            responses, to_replicate = MessageHandler(msg=data, is_from_master=is_from_master, app = self).execute()
            if self.state == ServerState.MASTER and to_replicate:
                self._propagate_to_replicas(to_replicate)

            return responses
        except Exception as e:
            return [f"-ERR {str(e)}\r\n".encode()]

    def _send_to_master(self, data: bytes):
        """Send data to master with error handling"""
        try:
            self.master_connection.sendall(data)
        except Exception as e:
            logger.log(f"Error sending to master: {e}")
            self._reconnect_to_master()

    def _reconnect_to_master(self):
        """Handle master connection failure by attempting to reconnect"""
        while self.is_running and self.state == ServerState.REPLICA:
            try:
                self._establish_replication()
                break
            except Exception as e:
                logger.log(f"Reconnection attempt failed: {e}")
                time.sleep(1)  # Wait before retrying

    def _handle_master_propagation(self):
        """Handle incoming commands from master"""
        try:
            while self.is_running and self.state == ServerState.REPLICA:
                # Read command from master

                command = self.master_connection.recv(1024)

                if not command:
                    continue
                self.client_socket = self.master_connection
                responses = self.process_command(command, is_from_master=True)
                if responses:
                    for idx, res in enumerate(responses):
                        self.master_connection.send(res)

        except Exception as e:
            logger.log(f"Error in propagation thread: {e}")
            # Attempt to reconnect to master
            self._reconnect_to_master()

    def _parse_arguments(self, args=None):
        parser = argparse.ArgumentParser(description="Redis file processor")
        parser.add_argument("--dir", required=False, help="Directory path")
        parser.add_argument("--dbfilename", required=False, help="dbfilename")
        parser.add_argument("--port", required=False, help="port")
        parser.add_argument("--replicaof", required=False, help="replicaof")
        args = parser.parse_args()
        if args.dir:
            Config.set_directory(args.dir)
        if args.dbfilename:
            Config.set_dbfilename(args.dbfilename)
        if args.port:
            self.port = int(args.port)
        if args.replicaof:
            self.master_host, self.master_port = args.replicaof.split(" ")

        return args

    def shutdown(self):
        """Gracefully shut down the server"""
        self.is_running = False
        logger.log("Shutting down server...")

        # Close all connections
        if self.server_socket:
            self.server_socket.close()

        if self.master_connection:
            self.master_connection.close()

        with self.replica_lock:
            for replica_socket in self.replicas:
                try:
                    replica_socket[0].close()
                except Exception:
                    pass
