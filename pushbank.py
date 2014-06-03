#-*- coding: utf-8 -*-
"""
PushBank - Bank account balance change detector
Copyright 2014, ssut
Licensed under the MIT License.
"""
import logging
import os
import sys
from textwrap import dedent as trim

def create_default_config(fn):
    f = open(fn, 'w')
    print >> f, trim("""\
    #-*- coding: utf-8 -*-
    EMAIL = {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': 587,
        'SMTP_USER': '',
        'SMTP_PASSWORD': '',
        'SMTP_TLS': True,
        'TARGET': '',
        'TITLE': u'{bank_name} 예금액 변동 알림',
    }

    BANK = {
        'kbstar': {
            'account': '',
            'password': '',
            'resident': '',
            'username': '',
        }
    }
    """)
    f.close()

def main():
    config_file = os.path.join('.', 'config.py')
    tmp_dir = os.path.join('.', 'tmp')
    if not os.path.isfile(config_file):
        create_default_config(config_file)
        print >> sys.stdout, 'Created config file. Edit config.py and run pb again'
        sys.exit(0)
    if not os.path.isdir(tmp_dir):
      os.mkdir(tmp_dir, 0777)

    try:
        import config
    except:
        pritn >> sys.stderr, 'Error: Could not import a config file!'
        sys.exit(1)

    import optparse
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help="Increase verbosity (specify multiple times for more)")
    opts, args = optp.parse_args()

    log_level = logging.WARNING
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    config.log_level = log_level

    from pushbank import PushBank
    PushBank.execute(config)

if __name__ == "__main__":
    main()