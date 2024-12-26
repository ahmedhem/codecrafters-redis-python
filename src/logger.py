import queue
import sys
import threading
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class Logger:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self._log_worker)
        self.log_thread.daemon = True
        self.is_running = True
        self.log_thread.start()

    def _log_worker(self):
        while self.is_running:
            try:
                level, message = self.log_queue.get(timeout=1)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                formatted_message = f"[{timestamp}] : {message}"
                print(formatted_message, flush=True)
                sys.stdout.flush()  # Ensure immediate logger.loging
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logging error: {e}", flush=True)

    def log(self, message: str):
        self.log_queue.put((LogLevel.DEBUG.value, message))

    def shutdown(self):
        self.is_running = False
        self.log_thread.join()


logger = Logger()
