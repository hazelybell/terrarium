from flask import Flask

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

app = Flask(__name__)

bag = None

@app.route('/')
def hello_world():
    if bag is None:
        raise Exception("Bag unset!")
    return "\n".join(bag.get_logs())
