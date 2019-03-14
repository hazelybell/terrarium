#!/usr/bin/env python3

import sys

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import terrarium
import web
import bag_of_logging

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical
logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)

if __name__=="__main__":
    terrarium = terrarium.Terrarium()
    sched_let = gevent.spawn(terrarium.run_forever)
    greenlets = [sched_let]
    
    web_server = WSGIServer(('', 5000), web.app, handler_class=WebSocketHandler)
    web_let = gevent.spawn(web_server.serve_forever)
    greenlets.append(web_let)
    
    log_handler = bag_of_logging.BagHandler()
    logging.getLogger().addHandler(log_handler)
    web.bag = log_handler
    
    gevent.joinall(greenlets)
    CRITICAL("Ran out of things to do, exiting")
    sys.exit(0)
