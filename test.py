import threading
import sys
import queue
import time

def print_with_exclamation(user_input):
    time.sleep(10)
    print(user_input + "!")

def worker(task_queue, stop_event):
    while not stop_event.is_set():
        try:
            task = task_queue.get(timeout=1)
        except queue.Empty:
            continue
        print_with_exclamation(task)
        task_queue.task_done()

def main():
    task_queue = queue.Queue()
    stop_event = threading.Event()
    worker_thread = threading.Thread(target=worker, args=(task_queue, stop_event))
    worker_thread.start()

    try:
        while True:
            sys.stdout.write("user> ")
            sys.stdout.flush()
            user_input = input().strip()

            if user_input.lower() == "exit":
                break

            task_queue.put(user_input)
    except KeyboardInterrupt:
        print("\nExiting due to KeyboardInterrupt...")

    stop_event.set()
    worker_thread.join()

if __name__ == "__main__":
    #main()
    mql=queue.Queue()
    for i in range(5):
       sing=i
       mql.put(sing)
    while(not mql.empty()):
        print(mql.get()) 

    