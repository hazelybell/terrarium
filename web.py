from flask import Flask

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
