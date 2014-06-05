#-*- coding: utf-8 -*-
import imp
import logging
import os
import pickle
import sys
import time
import traceback
import gevent

from gevent import monkey; monkey.patch_all()
from gevent import Greenlet
from gevent import queue
from gevent import sleep
from threading import current_thread
from jinja2 import Environment, FileSystemLoader

from .cache import Cache
from .mail import connect as connect_mail
from .mail import send as send_mail

home = os.getcwd()
class PushBank(object):
    def __init__(self, config):
        self.config = config
        self.emails = queue.Queue()
        self.adapters = {}
        self.cache = None
        self.template = Environment(loader=FileSystemLoader(os.path.join(
            home, 'pushbank', 'template'))).get_template('email.html')

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

        # load adapters
        self.load_adapter()

        # connect smtp server
        self.connected = connect_mail(server=config.EMAIL['SMTP_SERVER'],
                            port=config.EMAIL['SMTP_PORT'],
                            user=config.EMAIL['SMTP_USER'],
                            password=config.EMAIL['SMTP_PASSWORD'],
                            tls=config.EMAIL['SMTP_TLS'])

    @staticmethod
    def execute(config):
        pb = PushBank(config)
        # waiting for smtp server
        while not pb.connected:
            sleep(0)

        tmp_path = os.path.join(home, 'tmp')
        pb.cache = Cache(tmp_path=tmp_path)
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
                if not name in self.config.INCLUDE_BANKS: continue
                fn = os.path.join(home, 'adapters', fn)
                try: self.adapters[name] = imp.load_source(name, fn)
                except Exception, e:
                    traceback.print_exc()
                    print >> sys.stderr, "Error loading %s: %s" % (name, e)
                    sys.exit(1)

    def handle_adapter(self, adapter, **kwargs):
        current_thread().name = adapter.en_name.upper()
        result = adapter.query(**kwargs)
        if not 'history' in result:
            logging.warning('Missing history in query result')
            return
        result['history'].reverse()

        # generate balance, history cache key
        balance_key = '%s-balance' % (adapter.en_name)
        history_key = '%s-history' % (adapter.en_name)

        # get balance, histories from recently result
        latest_balance = result['balance']
        latest_history = result['history']

        # get balance from cache
        balance = self.cache.get(balance_key) if self.cache.exists(balance_key) \
                 else 0

        # if balance is already cached and different from the latest balance
        if balance > 0 and balance != latest_balance:
            latest_history_size = len(latest_history)
            # get histories from cache
            history = self.cache.get(history_key) if self.cache.exists(
                history_key) else []
            # check history diffs
            diffs = []
            # iterate from recently histories
            for h in latest_history:
                # serialize history element (for check of duplicate)
                serialized = pickle.dumps(h)
                # check exists of history in cached histories
                if not serialized in history:
                    diffs.append(h)
                    history.append(serialized)
                    # remove first element if greather than latest history size
                    if len(history) > latest_history_size:
                        history.pop(0)
            # save new history
            self.cache.set(balance_key, latest_balance)
            self.cache.set(history_key, history)
            # add email queue from diffs
            for data in diffs:
                self.emails.put({
                    'adapter': adapter,
                    'data': data,
                })
        elif balance > 0:
            logging.info('%s - No balance changes', adapter.en_name)
        else:
            # else save the balance and histories now
            history = []
            for h in latest_history:
                # serialize history element
                serialized = pickle.dumps(h)
                # add serialized history to history list
                history.append(serialized)
            # save to cache store
            self.cache.set(balance_key, latest_balance)
            self.cache.set(history_key, history)
            logging.info('Stored your bank account data such as' + \
                ' balance and history. Waiting for save data to disk..')

    def handle_bank(self):
        while True:
            bank_threads = []
            for name, kwargs in self.config.BANK.iteritems():
                if not name in self.config.INCLUDE_BANKS: continue
                adapter = self.adapters[name]
                thread = Greenlet.spawn(self.handle_adapter, adapter, **kwargs)
                thread.start()
                bank_threads.append(thread)

            gevent.joinall(bank_threads)
            for thread in bank_threads:
                del thread
            del bank_threads

            # check every 15 seconds
            sleep(15)

    def handle_email(self):
        while True:
            try:
                # get recent email item
                data = self.emails.get()
                adapter = data['adapter']
                history = data['data']
                mail_title = self.config.EMAIL['TITLE'].format(
                    bank_name=adapter.name,
                    bank_en_name=adapter.en_name)
                content = self.template.render(**history)
                send_mail(target=self.config.EMAIL['TARGET'], title=mail_title,
                    content=content, adapter_name=adapter.en_name)
            except queue.Empty:
                # sleep zero for yield
                sleep(0)
                continue
