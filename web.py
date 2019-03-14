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
cputemp = None

class WebSocketObserver:
    views = dict()
    
    def __init__(self, ws, observable, view_id):
        self.ws = ws
        assert observable is not None
        self.observable = observable
        self.observable.observe(self)
        self.oid = id(observable)
        if self.oid not in self.views:
            self.views[self.oid] = set()
        if view_id not in self.views[self.oid]:
            # either the page refreshed or the server restarted
            self.views[self.oid].add(view_id)
            self.refresh() # initial load, send full state
    
    def notify(self, e):
        if self.ws.closed:
            self.observable.unobserve(self)
            return
        self.ws.send(json.dumps(e))
    
    def refresh(self):
        self.observable.refresh(self)
    
@sockets.route('/log')
def log_socket(ws):
    logobserver = None
    cpuobserver = None
    while not ws.closed:
        message = ws.receive()
        message = json.loads(message)
        if 'viewID' in message:
            view_id = message['viewID']
            logobserver = WebSocketObserver(ws, bag, view_id)
            cpuobserver = WebSocketObserver(ws, cputemp, view_id)
        else:
            ValueError("Got bad command over websocket: " + str(message))

@app.route('/')
def index():
    return flask.send_file('static/index.html')

def hello_world():
    if bag is None:
        raise Exception("Bag unset!")
    return "\n".join(bag.get_logs())
