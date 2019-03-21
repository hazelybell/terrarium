# terrarium

Runs my terrarium from my Raspberry Pi.

## Features

* Web UI
    * Logging via customised logger
    * CPU Temperature
    * Soil Moisture
    * Outlet status
    * Flask
    * Single static page
    * Communicates via websockets
* Asynchronous
    * Single-threaded multi-tasking
    * Gevent
    * Deadline-oriented co-operative sleep scheduler
    * Supports sub-second timing
* Morse code
    * Comms light can be used for communication with morse code
* Self-updating
    * Restarts itself when changed pushed to Raspberry Pi
* Lamp
    * Controlls a lamp via [Automation Hat](https://shop.pimoroni.com/products/automation-hat) relay
    * Turns on and off at specified times of day
* Soil Moisture
    * Logs soil moisture readings
    * Two capacative probes
    * Uses Automation Hat's analog inputs
* Logging
    * Logs to console and web UI using Python's built-in logging framework
* Object-oriented
    * Observer pattern
    * Schedule events
    * Polling

## License
    Copyright (C) 2019 Hazel Victoria Campbell

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
