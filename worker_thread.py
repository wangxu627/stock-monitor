import threading

from job import run

worker_thread_started = False
worker_thread_lock = threading.Lock()

def start_worker_thread():
    global worker_thread_started

    with worker_thread_lock:
        if not worker_thread_started:
            workder_thread = threading.Thread(target=run)
            workder_thread.start()
            worker_thread_started = True