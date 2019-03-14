import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class BagHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().init(*args, **kwargs)
        self.records = list()
    
    def emit(record):
        formatted = self.format(record)
        self.records.append(formatted)