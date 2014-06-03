#-*- coding: utf-8 -*-
import imp
import logging
import os
import sys
import time
import traceback

import gevent
from gevent import monkey; monkey.patch_all()
from gevent import Greenlet
from gevent import queue
from gevent import sleep
from threading import current_thread

from .cache import Cache

home = os.getcwd()
class PushBank(object):
    def __init__(self, config):
        self.config = config
        self.emails = queue.Queue()
        self.adapters = {}
        tmp_path = os.path.join(home, 'tmp')
        self.cache = Cache(tmp_path=tmp_path)

        # pushbank logger
        current_thread().name = 'MAIN'
        root_logger = logging.getLogger()
        root_logger.level = config.log_level
        log_formatter = logging.Formatter('%(asctime)s [%(threadName)-8.8s]' + \
                                        ' [%(levelname)-5.5s]  %(message)s')
        file_handler = logging.FileHandler('tmp/stdout.log')
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        self.load_adapter()

    @staticmethod
    def execute(config):
        pb = PushBank(config)
        email_process = Greenlet.spawn(pb.handle_email)
        email_process.start()
        bank_process = Greenlet.spawn(pb.handle_bank)
        bank_process.start()

        try:
            gevent.joinall([email_process, bank_process])
        except KeyboardInterrupt:
            print >> sys.stdout, 'PushBank has stopped working'
            sys.exit(0)

    def load_adapter(self):
        banks = self.config.BANK.keys()
        for fn in os.listdir(os.path.join(home, 'adapters')):
            name = os.path.basename(fn)[:-3]
            if fn.endswith('.py') and not fn.startswith('_'):
                fn = os.path.join(home, 'adapters', fn)
                try: self.adapters[name] = imp.load_source(name, fn)
                except Exception, e:
                    traceback.print_exc()
                    print >> sys.stderr, "Error loading %s: %s" % (name, e)
                    sys.exit(1)

    def handle_bank(self):
        while True:
            for name, kwargs in self.config.BANK.iteritems():
                adapter = self.adapters[name]
                result = adapter.query(**kwargs)
            sleep(5)

    def handle_email(self):
        while True:
            try:
                data = self.emails.get()
            except queue.Empty:
                sleep(0)
                continue
            print data
