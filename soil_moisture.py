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

import time
import statistics

from observable import Observable
from schedule import Poller

import automationhat

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class SoilMoist(Poller, Observable):
    READINGS_GOOD = 20 # readings before considering the median good data
    READINGS_MAX = 30 # max n readings to take the median of
    READING_MIN = 0.5 # readings under this are considered bogus
    READING_MAX = 3.5 # readings over this are considered bogus
    
    def __init__(self, number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Observable.__init__(self)
        self.reading = None
        self.number = number
        self.min_read = 100
        self.max_read = -100
        self.time = None
        if number == 1:
            self.sensor = automationhat.analog.one
            self.max_ = 1.29
            self.min_ = 2.74
        elif number == 2:
            self.sensor = automationhat.analog.two
            self.max_ = 0.97
            self.min_ = 2.62
        elif number == 3:
            self.sensor = automationhat.analog.three
        else:
            raise ValueError("Bad soil moisture probe number")
    
    def read_analog(self):
        return self.sensor.read()
    
    def read_mean(self):
        readings = []
        while len(readings) < self.READINGS_GOOD:
            reading = self.read_analog()
            readings.append(reading)
            if (reading < self.READING_MIN
                or reading > self.READING_MAX
                ):
                WARNING("Bogus value from A/D converter: " + str(reading))
                return None
        if (max(readings) - min(readings) > 0.01):
            WARNING("Bogus range from A/D converter: " + 
                    str(max(readings)) + "-" + str(min(readings)))
            return None
        return statistics.mean(readings)
    
    def read_good(self):
        reading = None
        while reading is None:
            reading = self.read_mean()
        return reading
    
    def poll(self):
        reading = self.read_good()
        cur_time = time.time()
        if (self.reading != reading
            or self.time is None
            or cur_time - 60 > self.time):
            self.reading = reading
            self.time = cur_time
            self.notify_all()
    
    def json(self):
        while self.time is None:
            self.poll()
        pct = self.reading - self.min_
        pct = pct * 100 / (self.max_ - self.min_)
        return {
            'v': self.reading, 
            'pct': pct,
            'min': self.min_read,
            'max': self.max_read,
            'time': self.time
            }
    
