#!/usr/bin/env python3

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

import sys

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import terrarium
import web
import bag_of_logging
import storage

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical
logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)

def main():
    log_handler = bag_of_logging.BagHandler()
    logging.getLogger().addHandler(log_handler)
    web.observables['log'] = log_handler

    t = terrarium.Terrarium()
    sched_let = gevent.spawn(t.run_forever)
    greenlets = [sched_let]
    
    web.observables['cputemp'] = t.cputemp
    web.observables['lamp'] = t.lamp
    web.observables['sm1'] = t.sm_one
    web.observables['sm2'] = t.sm_two
    #web.observables['sm3'] = t.sm_three
    
    storage_ = storage.Storage(web.observables)
    web.storage = storage_
    
    web_server = WSGIServer(('', 5000), web.app, handler_class=WebSocketHandler)
    web_let = gevent.spawn(web_server.serve_forever)
    greenlets.append(web_let)
    
    gevent.joinall(greenlets)
    CRITICAL("Ran out of things to do, exiting")
    sys.exit(0)

if __name__=="__main__":
    main()
