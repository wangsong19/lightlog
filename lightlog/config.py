from os import getcwd as osgetcwd
import logging

DEFAULT_LOG_CONFIG = {
    ## log file name
    "fname": "",

    ## file path dir(use local server)
    "dir": osgetcwd(),

    ## default level
    "level": logging.INFO,

    ## rotating by when(default "Day")
    "when": "D",

    ## backup by week
    "backup_count": 7,

    ## use detail log or not
    "is_detail": False,

    ## log record formatter
    "fmt": "%(asctime)s[%(levelname)s] %(message)s",

    ## log record detail formatter
    "dfmt": "%(asctime)s[%(levelname)s][pid:%(process)d][tid:%(thread)d] %(message)s",

    ### --------------- use remote server
    ## use log server > address: ("localhost", 9939)
    "address": (),

    ## True/False: multi-process/multi-thread as server
    "is_mp": False, # default use thread
}

class LightConfig:

    ''' to load user log configuration '''

    instance = None
    
    def __init__(self):
        raise RuntimeError("-- LightConfig --:use `get_instance` function instaad of __init__")

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = object.__new__(cls)
            cls.instance.config = DEFAULT_LOG_CONFIG
        return cls.instance

    def load(self, config_dict):
        ''' load user configuration '''
        if type(config_dict) is not dict:
            raise TypeError("-- LightConfig --: type of lightlog config should be dict")
        for k, v in config_dict.items():
            if self.config.get(k) != None:
                self.config[k] = v
            if k == "address":
                import warnings
                warnings.warn(f"you are using {v} as log server to save log files" \
                        f"please ensure that you have set up log server on {v[0]}")

lightconfig = LightConfig.get_instance()
__all__ = ("lightconfig")
