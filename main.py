#!/usr/bin/env python3

import gevent
from gevent.pywsgi import WSGIServer

import terrarium
import web

if __name__=="__main__":
    terrarium = terrarium.Terrarium()
    sched_let = gevent.spawn(terrarium.run_forever())
    greenlets = [sched_let]
    
    web_server = WSGIServer(('', 5000), web.app)
    web_let = gevent.spawn(web_server.serve_forever())
    greenlets.append(web_let)
    
    gevent.joinall(greenlets)
    CRITICAL("Ran out of things to do, exiting")
    sys.exit(0)
