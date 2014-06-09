import logging
import os
import pickle
import time

from gevent import monkey; monkey.patch_all()
from gevent import sleep
from gevent import Greenlet
from threading import current_thread

from ._singleton import Singleton

class Cache(Singleton):
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.cache_file = os.path.join(tmp_path, 'cache.db')
        self._cache = {}
        self._modified = False
        self._backup_handler = Greenlet.spawn(self._backup_handler)

        self._reload()
        self._backup_handler.start()

    def _backup_handler(self):
        current_thread().name = 'BACKUP'
        while True:
            if self._modified:
                logging.info('Background saving started by backup_handler')
                start = time.clock()
                result = self._save()
                if result is True:
                    elapsed = (time.clock() - start) * 1000
                    logging.info('Cache saved on disk: %.3f seconds', elapsed)
            else:
                sleep(5)

    def _reload(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'r') as f:
                try:
                    self._cache = pickle.loads(f.read())
                except:
                    self._cache = {}
        else:
            self._cache = {}

    def _save(self):
        # waiting for write access permission to destination file
        while os.path.isfile(self.cache_file) and \
            not os.access(self.cache_file, os.W_OK):
            sleep(0.1)

        with open(self.cache_file, 'w') as f:
            try:
                dump = pickle.dumps(self._cache)
                f.write(dump)
                self._modified = False
                return True
            except:
                logging.warning('Cache save failed')
                return False

    def get(self, key):
        return (self._cache[key] if self.exists(key) else None)

    def set(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            for key, value in args[0].iteritems():
                self.set(key, value)
        elif len(args) == 2:
            self._cache[args[0]] = args[1]
            self._modified = True

    def exists(self, key):
        return (True if key in self._cache else False)
