from src.server import SocketServer

app = SocketServer()

if __name__ == "__main__":
    app.start_server()
