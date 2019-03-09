#!/usr/bin/env python3

import time
import datetime
import math
import sys

import automationhat

TIME_ON = datetime.time(hour=6, minute=30)
TIME_OFF = datetime.time(hour=21, minute=0)

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
        print("tick: " + str(cur_utime))
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
            sleep = next_utime - cur_utime
            print("Sleeping for " +  str(sleep))
            automationhat.light.power.write(0)
            time.sleep(sleep)
    
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
        print(morsed)
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

class Heartbeat(Schedule):
    TIME_ON = 0.5
    
    def beat(self):
        print("beat")
        automationhat.light.warn.write(1)
        self.then_after(self.TIME_ON, self.unbeat)
    
    def unbeat(self):
        automationhat.light.warn.write(1)
        self.next_second(self.beat)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #automationhat.light.on()
        self.next_second(self.beat)


if __name__=="__main__":
    if automationhat.is_automation_hat():
        pass
    else:
        raise ValueError("no automationhat")
    
    scheduler = Scheduler()
    morse = Morse(scheduler)
    Heartbeat(scheduler)
    morse.morse("start")
    scheduler.loop()
    print("Ran out of things to do, exiting")
    sys.exit(0)

#automationhat.light.on()

morse("ok")

while True:
    #automationhat.relay.one.toggle()
    #if automationhat.is_automation_hat():
    #    automationhat.relay.two.toggle()
    #    automationhat.relay.three.toggle()
    now = datetime.datetime.now()
    print(str(now));
    cur_time = now.time()
    print(str(cur_time))
    if cur_time > TIME_ON and cur_time < TIME_OFF:
        print("lights on")
        automationhat.relay.one.on()
    else:
        print("lights off")
        automationhat.relay.one.off()


