import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class BagHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = list()
    
    def emit(self, record):
        formatted = self.format(record)
        self.logs.append(formatted)
    
    def get_logs(self):
        return self.logs
