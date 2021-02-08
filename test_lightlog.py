import multiprocessing
import time
import signal
import os

from lightlog import (
        get_logger, 
        get_ready_log_worker, 
        LogServer,
        lightconfig)

# test for single process log
def print_log_second():
    logger = get_logger(fname="lightlog_test")
    i = 0
    while True:
        if i > 120: break
        time.sleep(1)
        logger.info("--- you have a new log message, please record it!", 
                i, " > Process-", os.getpid())
        i += 1

# test for multi-process log
def test_multi_process():
    # set log worker
    log_worker = get_ready_log_worker()
    log_worker.start()
    # set rabot to records log
    worker1 = multiprocessing.Process(target=print_log_second)
    worker1.start()
    worker2 = multiprocessing.Process(target=print_log_second)
    worker2.start()
    # shutdonw signal and join
    def handler(sig, f):
        worker1.kill()
        worker2.kill()
        log_worker.kill()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    worker1.join()
    worker2.join()
    log_worker.join()

# test for remote log server
def test_log_server():
    config_dict = {"address": ("0.0.0.0", 9939), "is_mp": False}
    lightconfig.load(config_dict)
    # set up server
    server_porcess = multiprocessing.Process(target=start_server_process)
    server_porcess.start()
    # set up client
    worker1 = multiprocessing.Process(target=print_log_second)
    worker1.start()
    worker2 = multiprocessing.Process(target=print_log_second)
    worker2.start()
    # shutdonw signal and join
    def handler(sig, f):
        worker1.kill()
        worker2.kill()
        server_porcess.kill()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    worker1.join()
    worker2.join()
    server_porcess.join()
    
def start_server_process():
    ''' copy from super-Process '''
    LogServer.run()

if __name__ == "__main__":
    print_log_second()
    #test_multi_process()
    #test_log_server()
    pass
