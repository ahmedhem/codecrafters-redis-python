import threading
from threading import Thread
import queue
import time


class TaskQueue:
    def __init__(self, num_workers=1):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.start()

    def worker(self, thread_id):
        while True:
            try:
                task = self.task_queue.get()
                if not task:
                    continue
                task()
            except queue.Empty:
                continue
            except Exception as e:
                raise

    def add_task(self, task):
        self.task_queue.put(task)
        self.task_queue.task_done()

    def start(self):
        for i in range(self.num_workers):
            thread = threading.Thread(target=self.worker, args=(i,))
            thread.start()
