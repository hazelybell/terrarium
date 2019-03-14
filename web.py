import json

import flask
import flask_sockets

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)

bag = None

class WebSocketObserver:
    def __init__(self, ws, observable):
        self.ws = ws
        self.observable = observable
        self.observable.observe(self)
    
    def notify(self, e):
        if self.ws.closed:
            self.observable.unobserve(self)
            return
        self.ws.send(json.dumps(e))

@sockets.route('/log')
def log_socket(ws):
    observer = WebSocketObserver(ws, bag)

@app.route('/')
def index():
    return flask.send_file('static/index.html')

def hello_world():
    if bag is None:
        raise Exception("Bag unset!")
    return "\n".join(bag.get_logs())
