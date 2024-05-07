import time
import matplotlib.pyplot as plt
import numpy as np

import multiprocessing 

# Initialize global variables outside of any function
start_time = time.time()
lock = multiprocessing.Lock()
count_dict = {}

def worker(wait_time, count):
    global count_dict
    global lock
    print(f"Worker entered: {time.time()-start_time} ms")
    time.sleep(wait_time/1000)
    lock.acquire()
    try:
        count_dict[count] = wait_time
    finally:
        lock.release()  # Ensure the lock is always released
    print(f"Worker finished: {time.time()-start_time}")

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=worker, args=(300, 3))
    p1.start()
    p1.join()

    print(count_dict)

    # Use plt.pause(0) to allow the plot to be displayed without blocking
    plt.pause(0)

   



