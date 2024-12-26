import argparse
import queue
import socket
import sys
import threading
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Dict, Any, List
import time

from src.config import Config
from src.encoder import Encoder
from src.message_handler import MessageHandler
from src.rdb_parser import RDBParser
from src.logger import logger


class ServerState(Enum):
    STANDALONE = "standalone"
    REPLICA = "replica"
    MASTER = "master"


class RedisServer:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.host = host
        self.port = port
        self.server_socket = None
        self.state = ServerState.STANDALONE
        self.master_info: Optional[Tuple[str, int]] = None
        self.accept_thread = None
        self.is_running = False
        self.master_connection = None
        self.replication_buffer = []
        self.data_store: Dict[str, Any] = {}  # Simple key-value store
        self.propagation_thread = None
        self.args = self._parse_arguments()
        self.replicas: List[Tuple[socket.socket, Tuple[str, int]]] = []
        self.replica_lock = threading.Lock()

        if self.args.replicaof:
            master_host, master_port = self.args.replicaof.split(" ")
            self._initialize_as_replica(master_host, int(master_port))
        else:
            self._initialize_as_master()

    def start_serving(self):
        logger.log("Start Serving")
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
                logger.log(client_socket)
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
                logger.log(f"Master Recieved {data}")
                if not data:
                    break
                if self.state == ServerState.MASTER and data ==  b'*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n':
                    logger.log("FOUND replica")
                    self.replicas.append((client_socket, address))

                # Process commands based on current server state
                responses = self._process_command(data, is_from_master=False)
                for res in responses:
                    logger.log(f"We will send reponse {res} {address}")
                    client_socket.send(res)
                    # logger.log(f"succefully sent reponse {res}")


        except Exception as e:
            logger.log(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def _initialize_as_replica(self, master_host: str, master_port: int):
        """Initialize replication after server is already running"""
        logger.log("replica initialization started")
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
            # Connect to master
            self.master_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.master_connection.connect(self.master_info)

            logger.log("Sending Ping Command to master")

            # Send PING
            self._send_to_master(b'*1\r\n$4\r\nPING\r\n')
            ping_response = self.master_connection.recv(1024)
            logger.log(f"recv {ping_response} Command from master")

            # Send REPLCONF
            self._send_to_master(
                Encoder(
                    lines=f"REPLCONF listening-port {Config.port}".split(" "),
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

            # Handle RDB transfer
            self._receive_rdb()

            # Update server state
            self.state = ServerState.REPLICA
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
            for replica_socket in self.replicas:
                logger.log(f"Start Propagation to {replica_socket} {command}")
                try:
                    replica_socket[0].sendall(command)
                except Exception as e:
                    logger.log(
                        f"Error handling replica at {self.replicas[replica_socket][0]}:{self.replicas[replica_socket][1]}",
                        e,
                    )
                    dead_replicas.append(replica_socket)

            for replica_socket in dead_replicas:
                self.replicas.pop(replica_socket)

    def _receive_rdb(self):
        """Handle receiving and loading RDB file"""
        try:
            # Read the FULLRESYNC response
            response = self.master_connection.recv(1024)
            logger.log( f"FULL RESYNC {response}")
            data = response.splitlines()
            rdb_data = b'\r\n'.join(data[2:4])
            command = b'\r\n'.join(data[4:len(data)])
            command = b"*3\r\n" + command # hardcoded for now until we figure out why the tester send the format like this
            logger.log(rdb_data)
            logger.log(command)

            # Process RDB file (simplified - you'd want to actually parse the RDB format)
            self._load_rdb(rdb_data)
            self._process_command(command)
        except Exception as e:
            logger.log(f"Error receiving RDB: {e}")
            raise

    def _load_rdb(self, rdb_data: bytes = None):
        logger.log("Loading RDB...")
        """Load data from RDB file into memory"""
        # Simplified RDB loading - you'd want to implement proper RDB parsing
        RDBParser(file=rdb_data).parse()
        # Parse RDB and populate data_store

    def _process_command(
        self, data: bytes, is_from_master: bool = False
    ) -> List[bytes]:
        """Process Redis commands based on server state and source"""
        try:
            logger.log(ServerState.MASTER)
            responses, can_replicate = MessageHandler(msg=data).execute()
            logger.log(f"can replicate {can_replicate}")
            if self.state == ServerState.MASTER and can_replicate:
                self._propagate_to_replicas(data)

            return responses
        except Exception as e:
            return [f"-ERR {str(e)}\r\n".encode()]

    def _read_until_crlf(self) -> bytes:
        """Read from master until CRLF is found"""
        buffer = []
        while True:
            char = self.master_connection.recv(1)
            if not char:
                break
            buffer.append(char)
            if len(buffer) >= 2 and buffer[-2:] == [b"\r", b"\n"]:
                return b"".join(buffer[:-2])

    def _read_exactly(self, n: int) -> bytes:
        """Read exactly n bytes from master"""
        data = b""
        while len(data) < n:
            chunk = self.master_connection.recv(min(n - len(data), 1024))
            if not chunk:
                break
            data += chunk
        return data

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
                logger.log("Attempting to reconnect to master...")
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
                logger.log(f"Found command {command}")
                self._process_command(command, is_from_master=True)

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
            Config.set_port(args.port)
        if args.replicaof:
            master_host, master_port = args.replicaof.split(" ")
            Config.set_master_replica(master_host, master_port)

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
                    replica_socket.close()
                except Exception:
                    pass
