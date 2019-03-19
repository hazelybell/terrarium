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
    
class Poller:
    def __init__(self, heartbeat):
        self.heartbeat = heartbeat
        heartbeat.add_poller(self)

