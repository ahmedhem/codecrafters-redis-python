import threading
import time


def task1():
    while True:
        with threading.Lock():
            print("Task 1: Processing data...")
        time.sleep(2)