import time

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class JsonFormatter(logging.Formatter):
    def format(record):
        o = {
            'level': record.levelname,
            'pathname': record.pathname,
            'lineno': record.lineno,
            'msg': record.getMessage(),
            'func': record.funcName,
            'time': record.created,
            'module': record.module,
        }
        return o

class BagHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(JsonFormatter)
        self.logs = list()
        self.observers = set()
    
    def emit(self, record):
        formatted = self.format(record)
        self.logs.append(formatted)
        if len(self.logs) > 1000:
            self.logs.pop(0)
        for observer in [self.observers]: # make a copy here
            observer.notify(formatted)
    
    def get_logs(self):
        return self.logs
    
    def observe(self, observer):
        self.observers.add(observer)
    
    def unobserve(self, observer):
        self.observers.remove(observer)
