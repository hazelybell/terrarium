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


import datetime
import math
import sys
import os
import time
import subprocess
import statistics

import automationhat
import gevent
from gevent import sleep

from observable import Observable

LAMP_TIME_ON = datetime.time(hour=6, minute=30)
LAMP_TIME_OFF = datetime.time(hour=21, minute=0)

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-', ' ':' '}

class Schedulable:
    def __init__(self, when, fn):
        assert isinstance(when, float) or isinstance(when, int)
        self.utime = when
        self.run = fn

class Schedule:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.scheduler.add(self)
        self.queue = []
    
    def add(self, schedable):
        if len(self.queue) > 0:
            assert(self.queue[-1].utime <= schedable.utime)
        self.queue.append(schedable)
    
    def then_after(self, seconds, what):
        if len(self.queue) > 0:
            prev = self.queue[-1].utime
        else:
            prev = time.time()
        when = prev + seconds
        schedable = Schedulable(when, what)
        self.add(schedable)
    
    def next_second(self, what):
        when = int(time.time()) + 1
        schedable = Schedulable(when, what)
        self.add(schedable)
    
class Scheduler:
    def __init__(self):
        self.schedules = set()
    
    def tick(self):
        cur_utime = time.time()
        #DEBUG("tick: " + str(cur_utime))
        next_utime = math.inf
        for schedule in self.schedules:
            i = 0;
            while i < len(schedule.queue):
                schedulable = schedule.queue[i]
                if schedulable.utime < cur_utime:
                    schedulable.run()
                    schedule.queue.pop(i)
                else:
                    if schedulable.utime < next_utime:
                        next_utime = schedulable.utime
                    i += 1
        return next_utime
    
    def loop(self):
        while True:
            next_utime = self.tick()
            if next_utime == math.inf:
                return
            # go to sleep and loop
            cur_utime = time.time()
            sleep_time = next_utime - cur_utime
            if sleep_time > 0:
                #DEBUG("Sleeping for " +  str(sleep_time))
                sleep(sleep_time)
    
    def add(self, schedule):
        self.schedules.add(schedule)
    
class Morse(Schedule):
    TIME_UNIT = 0.5
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_s = '>'
    
    def on(self):
        automationhat.light.comms.write(1)
    def off(self):
        automationhat.light.comms.write(0)

    def emit_dash(self):
        if self.prev_s == '.' or self.prev_s == '-':
            self.then_after(self.TIME_UNIT, self.on) # inter-symbol space
        elif self.prev_s == ' ' or self.prev_s == '_':
            pass # we already had a space
        else:
            raise ValueError("Invalid morse sequence")
        self.then_after(self.TIME_UNIT * 3, self.off) # dash
        self.prev_s = '-'

    def emit_dot(self):
        if self.prev_s == '.' or self.prev_s == '-':
            self.then_after(self.TIME_UNIT, self.on) # inter-symbol space
        elif self.prev_s == ' ' or self.prev_s == '_':
            pass # we already had a space
        else:
            raise ValueError("Invalid morse sequence")
        self.then_after(self.TIME_UNIT, self.off) # dash
        self.prev_s = '.'
    
    def emit_letter_space(self):
        if self.prev_s == '.' or self.prev_s == '-':
            self.then_after(self.TIME_UNIT * 3, self.on)
        else:
            raise ValueError("Invalid morse sequence")
        self.prev_s = '_'

    def emit_word_space(self):
        if self.prev_s == '.' or self.prev_s == '-' or self.prev_s == '>':
            self.then_after(self.TIME_UNIT * 7, self.on)
        else:
            raise ValueError("Invalid morse sequence")
        self.prev_s = ' '
    
    def start_message(self):
        assert self.prev_s == '>'
        self.then_after(self.TIME_UNIT * 7, self.on)
        self.prev_s = ' '
    
    def end_message(self):
        if self.prev_s == '.' or self.prev_s == '-':
            pass # we already turned off
        else:
            raise ValueError("Invalid morse sequence")
        self.then_after(self.TIME_UNIT * 7, self.off) # make sure there's a good space between messages
        self.prev_s = '>'

    def morse(self, msg):
        msg = msg.upper()
        morsed = ""
        for i in range(0, len(msg)):
            morsed = morsed + MORSE_CODE_DICT[msg[i]]
            if i + 1 < len(msg) and msg[i+1] != ' ':
                morsed = morsed + '_'
            elif i + 1 >= len(msg):
                morsed = morsed + ' .-.-.' # AR: end of message
            elif i + 1 < len(msg) and msg[i+1] == ' ':
                pass
        self.emit_morse(morsed)
    
    def emit_morse(self, morsed):
        INFO(morsed)
        self.start_message()
        for c in morsed:
            if c == '.':
                self.emit_dot()
            elif c == '-':
                self.emit_dash()
            elif c == '_':
                self.emit_letter_space()
            elif c == ' ':
                self.emit_word_space()
            else:
                raise ValueError("Invalid morse sequence: " + morsed)
        self.end_message()

class Poller:
    def __init__(self, heartbeat):
        self.heartbeat = heartbeat
        heartbeat.add_poller(self)

class Heartbeat(Schedule):
    TIME_ON = 0.1
    MAX_LEVEL = 0.1
    
    def poll(self):
        #DEBUG("beat")
        for poller in self.pollers:
            poller.poll()
    
    def add_poller(self, poller):
        self.pollers.add(poller)

    def glowup(self, level):
        def glow():
            automationhat.light.power.write(self.MAX_LEVEL*level)
        return glow
    
    def beat(self):
        STEPS = 1
        self.poll()
        for i in range(1, STEPS+1):
            if i == 1:
                # this is the first brigtness change we can do it now
                self.glowup(i/STEPS)()
            else:
                self.then_after(self.TIME_ON, self.glowup(i/STEPS))
        for i in range(1, STEPS+1):
            self.then_after(self.TIME_ON, self.glowup((STEPS-i)/STEPS))
        self.next_second(self.beat)
    
    def unbeat(self):
        automationhat.light.power.write(0)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        automationhat.light.power.write(1)
        self.next_second(self.beat)
        self.pollers = set()

class Outlet(Poller, Observable):
    def __init__(self, time_on, time_off, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Observable.__init__(self)
        self.time_on = time_on
        self.time_off = time_off
    
    def poll(self):
        cur_time = datetime.datetime.now().time()
        if cur_time > self.time_on and cur_time < self.time_off:
            if automationhat.relay.one.is_off():
                INFO("turning outlet on")
            automationhat.relay.one.on()
            self.notify_all()
        else:
            if automationhat.relay.one.is_on():
                INFO("turning outlet off")
            automationhat.relay.one.off()
            self.notify_all()
    
    def json(self):
        if automationhat.relay.one.is_on():
            return {'power': 'on'}
        else:
            return {'power': 'off'}

class SelfUp(Poller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = dict()
        for m in sys.modules.values():
            if hasattr(m, "__file__"):
                f = m.__file__
                self.files[f] = os.stat(f).st_mtime
    
    def poll(self):
        for f, original_mtime in self.files.items():
            new_mtime = os.stat(f).st_mtime
            if new_mtime != original_mtime:
                INFO(f + ' changed')
                args = sys.argv[:]
                args.insert(0, sys.executable)
                INFO('Re-spawning %s' % ' '.join(args))
                os.execv(sys.executable, args)
                raise Exception('Unreachable')

class CPUTemp(Poller, Observable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Observable.__init__(self)
        self.temp = None
    
    def poll(self):
        r = subprocess.check_output(
            ["/opt/vc/bin/vcgencmd", "measure_temp"], 
            )
        r = r.decode()
        r = r.replace("temp=", "")
        r = r.replace("'C\n", "")
        r = float(r)
        if r != self.temp:
            self.temp = r
            self.notify_all()
    
    def json(self):
        return {'temp': self.temp}

class SoilMoist(Poller, Observable):
    def __init__(self, number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Observable.__init__(self)
        self.readings = []
        self.number = number
        self.median = 0
        self.min_med = 100
        self.max_med = -100
        if number == 1:
            self.sensor = automationhat.analog.one
            self.max_ = 1.29
            self.min_ = 2.74
        elif number == 2:
            self.sensor = automationhat.analog.two
        elif number == 3:
            self.sensor = automationhat.analog.three
        else:
            raise ValueError("Bad soil moisture probe number")
    
    def read(self):
        reading = self.sensor.read()
        self.readings.append(reading)
        if len(self.readings) > 100:
            self.readings.pop(0)
        median = statistics.median(self.readings)
        #DEBUG("Soil moisture reading #" + str(self.number)
              #+ ": " + str(reading)
              #+ " median " + str(median)
              #)
        return median
    
    def poll(self):
        self.read()
        median = self.read()
        if len(self.readings) > 90:
            if median < self.min_med:
                self.min_med = median
            if median > self.max_med:
                self.max_med = median
        if median != self.median:
            self.median = median
            self.notify_all()
    
    def json(self):
        pct = self.median - self.min_
        pct = pct * 100 / (self.max_ - self.min_)
        return {
            'v': self.median, 
            'pct': pct,
            'min': min_med,
            'max': max_med,
            }
    
    
class Terrarium:
    __instance = None
    def __init__(self):
        assert self.__instance is None
        self.__instance = self
        if automationhat.is_automation_hat():
            pass
        else:
            raise ValueError("no automationhat")
        self.scheduler = Scheduler()
        self.morse = Morse(self.scheduler)
        self.heartbeat = Heartbeat(self.scheduler)
        self.selfup = SelfUp(self.heartbeat)
        self.lamp = Outlet(LAMP_TIME_ON, LAMP_TIME_OFF, self.heartbeat)
        self.cputemp = CPUTemp(self.heartbeat)
        self.sm_one = SoilMoist(1, self.heartbeat)
        
        self.morse.morse("start")
    
    def run_forever(self):
        self.scheduler.loop()
        raise Exception('Unreachable')




