#!/usr/bin/env python

import time
import datetime

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

def morse(msg):
    msg = msg.upper()
    morsed = "  "
    for i in range(0, len(msg)):
        morsed = morsed + MORSE_CODE_DICT[msg[i]]
        if i + 1 < len(msg) and msg[i+1] != ' ':
            morsed = morsed + '_'
        elif i + 1 >= len(msg):
            morsed = morsed + ' .-.-. ' # AR: end of message
        elif i + 1 < len(msg) and msg[i+1] == ' ':
            pass
    print(morsed)
    TIME_UNIT = 0.5
    for c in morsed:
        if c == '-':
            automationhat.light.comms.write(1)
            time.sleep(TIME_UNIT * 3)
            automationhat.light.comms.write(0)
            time.sleep(TIME_UNIT * 1)
        elif c == '.':
            automationhat.light.comms.write(1)
            time.sleep(TIME_UNIT * 1)
            automationhat.light.comms.write(0)
            time.sleep(TIME_UNIT * 1)
        elif c == '_':
            automationhat.light.comms.write(0)
            time.sleep(TIME_UNIT * 3)
        elif c == ' ':
            automationhat.light.comms.write(0)
            time.sleep(TIME_UNIT * 7)

if automationhat.is_automation_hat():
    pass
else:
    raise ValueError("no automationhat")

#automationhat.light.on()
morse("ok")

while True:
    #automationhat.relay.one.toggle()
    #if automationhat.is_automation_hat():
    #    automationhat.relay.two.toggle()
    #    automationhat.relay.three.toggle()
    automationhat.light.power.write(1)
    time.sleep(0.05)
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

    # go to sleep and loop
    cur_utime = time.time()
    sleep = int(cur_utime + 1) - cur_utime
    print("Sleeping for " +  str(sleep))
    automationhat.light.power.write(0)
    time.sleep(sleep)

