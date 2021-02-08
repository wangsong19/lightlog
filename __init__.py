''' lightlog

    support multi-processing log tasks.
    1. send record to local log process and save it as local file log.
    2. send record to log server and save it in log server disk.

    usage:
        a. set user-self log as configurations and use lightcofig to load it
            *fill address when we use log server, and `python log.py`
            on log server, it will listen specific port to work,
            *if address is (), unlight2 will start log process as dae-
            mon process to save records on local disk.

            >>> import lightlog
            
            >>> config = lightlog.get_instance()
            >>> config.load(my_config_dict)
            
            then if you use it in:
                single process: just `lightlog.get_logger()` to print you record
                    >>> task_log = lightlog.get_logger(fname="task")
                    >>> task_log.info("player one just finishs new-player task..")

                multi-process: provide one queue to log process
                    # main-process
                    >>> log_worker = lightlog.get_ready_log_worker()
                    >>> log_worker.start()
                    >>> log_worker.join()
                    
                    # sub-process
                    >>> task_log = lightlog.get_logger(fname="task")      # process-1
                    >>> task_log = lightlog.get_logger(fname="task")      # process-2
                    >>> task_log.info("player one just finishs new-player task..")

                remote-log-server: config address in user-config-dict, then loads it
                    >>> config_dict = {"address": ("192.168.9.99", 9939)}
                    >>> config = lightlog.get_instance()
                    >>> config.load(config_dict)
                    
                    then set up the lightlog server on 192.168.9.99 machine
                    also you can set configuration to use it as multi-process or multi-thread
                    default is multi-thread to handle log record request
                    if you use it as multi-processing, just do this:
                    >>> config_dict = {
                    >>>     "address": ("192.168.9.99", 9939),
                    >>>     "is_mp": True}
                    >>> server = lightlog.LogServer.run()
                    
        b. happy to use it.
'''

import .lightconfig
import .lightlog
__all__ = ["lightconfig", "get_logger", "get_ready_log_worker", "LogServer"]
