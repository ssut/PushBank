# -*- coding: utf-8 -*-
import imp
import logging
import os
import pickle
import sys
import time
import traceback
import eventlet
eventlet.monkey_patch()

from threading import current_thread
from jinja2 import Environment, FileSystemLoader

from .cache import Cache
from .mail import connect as connect_mail
from .mail import send as send_mail

home = os.getcwd()

# eventlet version of joinall similar to gevent one
def joinall(threads):
    for t in threads:
        try:
            t.wait()
        except:
            pass

class PushBank(object):

    def __init__(self, config):
        self.config = config
        self.emails = eventlet.queue.Queue()
        self.adapters = {}
        self.cache = None
        self.template = Environment(loader=FileSystemLoader(os.path.join(
            home, 'pushbank', 'template'))).get_template('email.html')

        # logger
        current_thread().name = 'MAIN'
        root_logger = logging.getLogger()
        root_logger.level = config.log_level
        log_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-8.8s]"
            " [%(levelname)-5.5s]  %(message)s")
        file_handler = logging.FileHandler('tmp/stdout.log')
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        # load adapters
        self.load_adapter()

        # connect to smtp server
        self.connected = connect_mail(server=config.EMAIL['SMTP_SERVER'],
                                      port=config.EMAIL['SMTP_PORT'],
                                      user=config.EMAIL['SMTP_USER'],
                                      passwd=config.EMAIL['SMTP_PASSWORD'],
                                      tls=config.EMAIL['SMTP_TLS'])

    @staticmethod
    def execute(config):
        pb = PushBank(config)
        # waiting for smtp to be ready
        while not pb.connected:
            eventlet.sleep(0)

        tmp_path = os.path.join(home, 'tmp')
        pb.cache = Cache(tmp_path=tmp_path)
        email_process = eventlet.spawn(pb.handle_email)
        bank_process = eventlet.spawn(pb.handle_bank)

        try:
            joinall([email_process, bank_process])
        except KeyboardInterrupt:
            logging.info('Pushbank has stopped working.')
            return 0

        return 1

    def load_adapter(self):
        banks = self.config.BANK.keys()
        for fn in os.listdir(os.path.join(home, 'adapters')):
            name = os.path.basename(fn)[:-3]
            if fn.endswith('.py') and not fn.startswith('_'):
                if name not in self.config.INCLUDE_BANKS:
                    continue
                fn = os.path.join(home, 'adapters', fn)
                try:
                    self.adapters[name] = imp.load_source(name, fn)
                except Exception as e:
                    traceback.print_exc()
                    logging.error('Error loading %s: %s', name, e)
                    sys.exit(1)

    def handle_adapter(self, adapter, **kwargs):
        current_thread().name = adapter.en_name.upper()
        try:
            result = adapter.query(**kwargs)
        except:
            logging.warning('%s - Failed to fetch data.', adapter.en_name)
            return
        if 'history' not in result:
            logging.warning('No histories fetched.')
            return
        result['history'].reverse()

        # generate keys
        balance_key = '%s-balance' % (adapter.en_name)
        history_key = '%s-history' % (adapter.en_name)

        # get the latest data obtained from the last made
        latest_balance = result['balance']
        latest_history = result['history']

        # get the balance from the cache
        balance = self.cache.get(balance_key) if self.cache.exists(balance_key) \
            else 0

        # check the difference between old and new balance
        if balance > 0 and balance != latest_balance:
            latest_history_size = len(latest_history)
            # get histories from cache
            history = self.cache.get(history_key) if self.cache.exists(
                history_key) else []
            diffs = []
            # iterate from histories
            for h in latest_history:
                # serialize history element (to find duplicates)
                serialized = pickle.dumps(h)
                # check if history is already in cached
                if serialized not in history:
                    diffs.append(h)
                    history.append(serialized)
                    # remove first element if greather than latest_history_size
                    if len(history) > latest_history_size:
                        history.pop(0)
            # save new history
            self.cache.set(balance_key, latest_balance)
            self.cache.set(history_key, history)
            # put email data from diffs into queue
            for data in diffs:
                self.emails.put({
                    'adapter': adapter,
                    'data': data,
                })
        elif balance > 0:
            logging.info('%s - Balance has not changed.', adapter.en_name)
        else:
            # or save the data
            history = []
            for h in latest_history:
                # serialize history element
                serialized = pickle.dumps(h)
                # add serialized history to list
                history.append(serialized)
            # save to cache store
            self.cache.set(balance_key, latest_balance)
            self.cache.set(history_key, history)
            logging.info("Initialized. Saving data in progress.")

    def handle_bank(self):
        while True:
            bank_threads = []
            for name, kwargs in self.config.BANK.iteritems():
                if name not in self.config.INCLUDE_BANKS:
                    continue
                adapter = self.adapters[name]
                thread = eventlet.spawn(self.handle_adapter, adapter, **kwargs)
                bank_threads.append(thread)

            joinall(bank_threads)
            for thread in bank_threads:
                del thread
            del bank_threads

            eventlet.sleep(self.config.REFRESH_INTERVAL)

    def handle_email(self):
        while True:
            try:
                # get 
                data = self.emails.get_nowait()
                adapter = data['adapter']
                history = data['data']
                mail_title = self.config.EMAIL['TITLE'].format(
                    bank_name=adapter.name,
                    bank_en_name=adapter.en_name)
                content = self.template.render(**history)
                send_mail(target=self.config.EMAIL['TARGET'], title=mail_title,
                          content=content, adapter_name=adapter.en_name)
            except eventlet.queue.Empty:
                eventlet.sleep(1)
                continue
