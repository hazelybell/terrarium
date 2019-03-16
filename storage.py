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

import sqlite3

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class StorageObserver:
    def __init__(self, storage, name, observable):
        self.name = name
        self.storage = storage
        self.observable = observable
        c = self.storage.conn.cursor()
        command = (
            "CREATE TABLE IF NOT EXISTS "
            + name
            + " (time real)"
            )
        c.execute(command)
        
        json = self.observable.json()
        for k, v in json.items():
            col = k + " "
            if isinstance(v, str):
                col = col + "text"
            elif isinstance(v, int) or isinstance(v, float):
                col = col + "real"
            command = "ALTER TABLE " + name + " ADD COLUMN " + col
            try:
                c.execute(command)
            except sqlite3.OperationalError as e:
                if 'duplicate column' in str(e):
                    pass
                else:
                    raise e
        self.conn.commit()
        self.observable.observe(self)
        self.refresh()
    
    def store(self, e):
        c = self.storage.conn.cursor()
        cols = []
        vals = []
        placeholders = []
        for col, val in e.items():
            cols.append(col)
            vals.append(val)
            placeholds.append("?")
        command = (
            "INSERT INTO " + self.name 
            + " (" + ", ".join(cols) + ") "
            + "VALUES (" + ", ".join(placeholders) + ")"
            )
        c.execute(command, vals)
        self.storage.conn.commit()
        
    
    def notify(self, e):
        if isinstance(e, list):
            for i in e:
                self.store(i)
        else:
            self.store(e)
    
    def refresh(self):
        self.observable.refresh(self)



class Storage:
    def create(self):
        for name, o in self.observables.items():
            observer = StorageObserver(self, name, o)
            
        
    def __init__(self, observables):
        self.observables = observables
        self.observers = []
        self.conn = sqlite3.connect('terrarium.sqlite3')
        self.create()
