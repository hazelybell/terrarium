#!/usr/bin/env python3

import gevent

import terrarium

if __name__=="__main__":
    terrarium = terrarium.Terrarium()
    sched_let = gevent.spawn(terrarium.run_forever())
    greenlets = [sched_let]
    gevent.joinall(greenlets)
    CRITICAL("Ran out of things to do, exiting")
    sys.exit(0)
