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
            'func': recordfunc,
            'time': record.created,
            'module': record.module,
        }
        j = json.dumps(o)
        return j

class BagHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(JsonFormatter)
        self.logs = list()
    
    def emit(self, record):
        formatted = self.format(record)
        self.logs.append(formatted)
    
    def get_logs(self):
        return self.logs
