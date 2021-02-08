from os import (
        getcwd as osgetcwd,
        path as ospath, 
        access as osaccess, 
        W_OK as osW_OK)
from sys import (
        stdout,
        stderr)
import logging
from logging.handlers import (
        QueueHandler, 
        SocketHandler, 
        TimedRotatingFileHandler)
from socketserver import (
        StreamRequestHandler,
        ThreadingTCPServer,
        ForkingTCPServer)
from struct import unpack as sunpack
from pickle import loads as ploads

from .config import lightconfig
config_dict = lightconfig.config


LOGGER_DICT = {}
def log_handle(fname, is_detail, queue=None):
    obj = LOGGER_DICT.get(fname)
    if obj:
        return obj
    logger = Logger(fname, is_detail, queue)
    LOGGER_DICT[logger] = logger
    return logger

def get_logger(fname=config_dict["fname"], is_detail=False):
    ''' get a specific file output record logger 
            :fname: output path file name
            :is_detail: record formats as detial or not
    '''
    if not fname:
        raise ValueError("-- LogServer -- error:\nyou shold provide fname in log config_dict to load or specific it as param")
    return log_handle(fname, is_detail)

def get_ready_log_worker(fname=config_dict["fname"], is_detail=False):
    ''' used in local log multi-process and process safe
        e.g.  
            log_worker = lightlog.get_log_worker()
            log_worker.start()
            log_worker.join() # block main process
        return log_worker, logger
    '''

    if not fname:
        raise ValueError("-- LogServer -- error:\nyou shold provide fname in log config_dict to load or specific it as param")

    import signal
    from multiprocessing import Process, Queue

    queue = Queue(-1)
    logger = log_handle(fname=fname, is_detail=is_detail, queue=queue)
    log_worker = Process(target=process_logger, args=(queue,), daemon=True)
    signal.signal(signal.SIGINT, lambda s, f: log_worker.kill())
    signal.signal(signal.SIGTERM, lambda s, f: log_worker.kill())
    return log_worker, logger

def process_logger(queue):
    ''' handle multi-process log from queue
        log_worker = multiprocessing.Process(
                target=process_logger, args=(queue,), daemon=True)
        log_worker.start()
        log_worker.join()
    '''
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            if not logger.handlers:
                handler = TimedRotatingFileHandler(
                            record.name,
                            when=config_dict["when"],
                            backupCount=config_dict["backup_count"])
                logger.addHandler(handler)
            logger.handle(record)
        except Exception:
            raise Exception('-- LogServer -- error')

class Logger:
    ''' logger
        no queue: single process server, records files local(default)
        use queue: multi-process server, records files local by log process
        no address: single/multi-process server, records files remote server
    '''
    queue = None

    def __init__(self, fname, is_detail, queue=None):
        Logger.queue = queue
        dir_ = config_dict["dir"]
        if not (ospath.isdir(dir_) 
                or osaccess(dir_, osW_OK)):
            raise FileExistsError(f"logger dir {dir_} is not exists or is not writable")

        serve_address = config_dict["address"]
        level = config_dict["level"]
        fmt = config_dict["dfmt"] \
                if is_detail else config_dict["fmt"]

        # build logger
        logger = logging.Logger(fname)
        logger.setLevel(level)
        formatter = logging.Formatter(fmt)
        # to console
        console = logging.StreamHandler(stdout)
        console.setFormatter(formatter)
        # to file
        if serve_address: # use remote log server
            handler = SocketHandler(*serve_address)
        elif Logger.queue: # use local log process
            handler = QueueHandler(Logger.queue)
        else: # simple log
            handler = TimedRotatingFileHandler(
                    fname,
                    when=config_dict["when"],
                    backupCount=config_dict["backup_count"])
        #handler.encoding = "utf-8" # support utf8
        handler.setFormatter(formatter)
        logger.addHandler(console)
        logger.addHandler(handler)
        self.logger = logger

    def set_level(self, level=logging.INFO):
        self.logger.setLevel(level)

    def debug(self, *args):
        self.logger.debug(" ".join([str(v) for v in args]))

    def info(self, *args):
        self.logger.info(" ".join([str(v) for v in args]))

    def warning(self, *args):
        self.logger.warning(" ".join([str(v) for v in args]))

    def error(self, *args):
        self.logger.error(" ".join([str(v) for v in args]))


class RecordStreamHandler(StreamRequestHandler):
    ''' to handle record stream '''
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = sunpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen-len(chunk))

            record = self.unpickle(chunk)
            logger = logging.getLogger(record.name)
            if not logger.handlers:
                if config_dict.get("is_detail"):
                    formatter = logging.Formatter(config_dict["dfmt"])
                else:
                    formatter = logging.Formatter(config_dict["fmt"])
                handler = TimedRotatingFileHandler(
                            record.name,
                            when=config_dict["when"],
                            backupCount=config_dict["backup_count"])
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.handle(record)

    def unpickle(self, chunk):
        # python issue #14436! we should received record as dict
        # and add formatter for server log!
        dict_ = ploads(chunk) # !to dict!
        dict_["level"] = getattr(logging, dict_["levelname"])
        return logging.LogRecord(**dict_)
        
class RecordReceiver(ThreadingTCPServer):
    ''' multi-threading noblock server '''
    allow_reuse_address = True

    def __init__(self, 
            host,
            port,
            handler=RecordStreamHandler):
        ThreadingTCPServer.__init__(self, (host, port), handler)
        self.stop = 0
        self.timeout = 3
    
    def serve_until_stopped(self):
        import select
        stop = 0
        while not stop:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd: self.handle_request()
            stop = self.stop
    def shutdown(self):
        self.server_close()
        self.stop = 1

class RecordReceiverFork(ForkingTCPServer):
    ''' multi-processing noblock server(only Unix) '''
    allow_reuse_address = True

    def __init__(self, 
            host,
            port,
            handler=RecordStreamHandler):
        ForkingTCPServer.__init__(self, (host, port), handler)
        self.stop = 0
        self.timeout = 3
    
    def serve_until_stopped(self):
        import select
        stop = 0
        while not stop:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd: self.handle_request()
            stop = self.stop

    def shutdown(self):
        self.server_close()
        self.stop = 1

class LogServer:
    ''' log server for remote records
        >>> from lightlog import LogServer, lightconfig
        >>> lightconfig.load({"address": ("192.168.xx.xx", 9939)}) # set `"is_mp": True` if use multi-p
        >>> LogServer.run() # start ok
    '''
                      
    @classmethod
    def run(cls):
        address = config_dict.get("address")
        if not address:
            raise ValueError("-- LogServer -- error:\n` config_dict.address ` is empty!")
        is_mp = config_dict.get("is_mp")
        level = config_dict.get("level")
        is_detail = config_dict.get("is_detail")
        fmt = config_dict.get("dfmt") \
                if is_detail else config_dict.get("fmt")

        logger = logging.getLogger()
        logger.setLevel(level)
        console = logging.StreamHandler(stdout)
        formatter = logging.Formatter(fmt)
        console.setFormatter(formatter)
        logger.addHandler(console)
        logger.info(f"log server start {address}...") 

        try:
            if is_mp:
                tcpserver = RecordReceiverFork(*address)
            else:
                tcpserver = RecordReceiver(*address)
            tcpserver.serve_until_stopped()
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("log server shutdown .. good bye~")
            tcpserver.server_close()

__all__ = ("get_logger", "get_ready_log_worker", "LogServer")
