#    This file is a part of terrarium: a software suite to manage my 
#    terrarium.
#    Copyright (C) 2019 Hazel Victoria Campbell
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

storage = None
observables = dict()

class WebSocketObserver:
    views = dict()
    
    def __init__(self, ws, observable, view_id, name):
        self.ws = ws
        assert observable is not None
        self.observable = observable
        self.view_id = view_id
        self.name = name
        self.observable.observe(self)
        self.oid = id(observable)
        if self.oid not in self.views:
            self.views[self.oid] = set()
        if view_id not in self.views[self.oid]:
            # either the page refreshed or the server restarted
            self.views[self.oid].add(view_id)
            self.refresh() # initial load, send full state
    
    def send(self, msg):
        try:
            self.ws.send(json.dumps(msg))
        except WebSocketError:
            self.observable.unobserve(self)
    
    def notify(self, e):
        if self.ws.closed:
            self.observable.unobserve(self)
            return
        if isinstance(e, list):
            named = [{self.name: v} for v in e]
            self.send(named)
        else:
            named = {self.name: e}
            self.send(named)
    
    def refresh(self):
        self.observable.refresh(self)
    
@sockets.route('/log')
def log_socket(ws):
    observers = list()
    while not ws.closed:
        message = ws.receive()
        if message is None:
            continue
        message = json.loads(message)
        if 'viewID' in message:
            view_id = message['viewID']
            for name, observable in observables.items():
                observer = WebSocketObserver(ws, observable, view_id, name)
        else:
            ValueError("Got bad command over websocket: " + str(message))

@app.route('/')
def index():
    return flask.send_file('static/index.html')

@app.route('/storage/<name>')
def get_storage(name):
    storage_observer = storage.observers[name]
    number = flask.request.args.get('number', None)
    records = None
    if number:
        records = storage_observer.last(number)
    else:
        abort(400) # Bad Request
    return flask.jsonify(records)

