# terrarium

Runs my terrarium from my Raspberry Pi.

## Features

* Web UI
    * Logging via customised logger
    * CPU Temperature
    * Outlet status
    * Flask
    * Communicates via websockets
* Asynchronous
    * Single-threaded multi-tasking
    * Gevent
    * Deadline-based sleep scheduler
* Morse code
    * Comms light can be used for communication with morse code
* Self-updating
    * Restarts itself when changed pushed to Raspberry Pi
* Lamp
    * Controlls a lamp via [Automation Hat](https://shop.pimoroni.com/products/automation-hat) relay
    * Turns on and off at specified times of day
