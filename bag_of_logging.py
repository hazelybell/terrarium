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

from observable import Observable

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

class JsonFormatter(logging.Formatter):
    def format(record):
        o = {
            'level': record.levelname,
            'pathname': record.pathname,
            'lineno': record.lineno,
            'msg': record.getMessage(),
            'func': record.funcName,
            'time': record.created,
            'module': record.module,
        }
        return o

class BagHandler(logging.Handler, Observable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Observable.__init__(self)
        self.setFormatter(JsonFormatter)
        self.logs = list()
    
    def emit(self, record):
        formatted = self.format(record)
        self.logs.append(formatted)
        if len(self.logs) > 1000:
            self.logs.pop(0)
        self.notify_all()
    
    def get_logs(self):
        return self.logs
    
    def json(self):
        return self.logs[-1]
    
    def refresh(self, observer):
        observer.notify(self.logs)
