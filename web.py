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
import flask_compress
import geventwebsocket

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

app = flask.Flask(__name__)
flask_compress.Compress(app)
app.config['COMPRESS_LEVEL'] = 1
sockets = flask_sockets.Sockets(app)

storage = None
observables = dict()

class WebSocketObserver:
    def __init__(self, ws, observable):
        self.ws = ws
        assert observable is not None
        self.observable = observable
        self.observable.observe(self)
    
    def notify(self, e):
        if self.ws.closed:
            self.observable.unobserve(self)
            return
        try:
            self.ws.send(json.dumps(e))
        except geventwebsocket.WebSocketError:
            self.observable.unobserve(self)
        
    

@app.route('/')
def index():
    return flask.send_file('static/index.html')

@app.route('/storage/<name>')
def get_storage(name):
    storage_observer = storage.observers[name]
    number = flask.request.args.get('number', None)
    since = flask.request.args.get('since', None)
    until = flask.request.args.get('until', None)
    records = None
    if number:
        records = storage_observer.last(number)
    elif since:
        records = storage_observer.since(since, until)
    else:
        abort(400) # Bad Request
    json = flask.jsonify(records)
    return json

@sockets.route('/observables/<name>')
def observable_socket(ws, name):
    if name not in observables:
        ws.close()
        WARNING("Remote end asked for bad observable " + name)
        return
    observer = WebSocketObserver(ws, observables[name])
    while not ws.closed:
        message = ws.receive()
        if message is None:
            continue
        message = json.loads(message)
        ValueError("Got bad command over websocket: " + str(message))
    

@app.route('/static/<path:path>')
def get_static(path):
    return send_from_directory('static', path)
