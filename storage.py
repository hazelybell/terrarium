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

class Storage:
    def create(self):
        c = self.conn.cursor()
        for name, o in self.observables:
            command = (
                "CREATE TABLE IF NOT EXISTS "
                + name
                + " (time real)"
                )
            c.execute(command)
            
            json = o.json()
            for k, v in json:
                col = k + " "
                if isinstance(v, str):
                    col = col + "text"
                elif isinstance(v, int) or isinstance(v, float):
                    col = col + "real"
                command = "ALTER TABLE " + name + " ADD COLUMN " + col
                try:
                    c.execute(command)
                except sqlite3.ProgrammingError as e:
                    WARN("ProgrammingError!")
                    raise e
            
        
    def __init__(self, observables):
        self.observables = observables
        self.conn = sqlite3.connect('terrarium.sqlite3')
        self.create()
