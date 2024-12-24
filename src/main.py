from src.server import app
from src.task_queue import TaskQueue
from src.workers.test import task1

if __name__ == "__main__":
    task_queue = TaskQueue(num_workers=4)
    task_queue.add_task(task1)
    app.start()
