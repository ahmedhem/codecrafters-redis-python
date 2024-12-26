from src.logger import logger
from src.server import RedisServer


if __name__ == "__main__":
    try:
        app = RedisServer()
        while True:
            pass
        # Your server code here
    except KeyboardInterrupt:
        app.shutdown()
        logger.shutdown()
