#-*- coding: utf-8 -*-
import logging
import smtplib
import sys

from email.mime.text import MIMEText
from email.header import Header
from gevent import monkey; monkey.patch_all()
from gevent import sleep

session = None
def connect(server='smtp.gmail.com', port=587, user='', password='', tls=False):
    global session
    session = smtplib.SMTP(server, port)
    session.ehlo()
    if tls: session.starttls()
    try:
        result = session.login(user, password)
        # check smtp login status (235, 270 = accepted)
        if result[0] != 235 and result[0] != 270 and not 'Accept' in result[1]:
            raise Exception('SMTP verification failed')
    except:
        logging.error('SMTP login failed')
        sys.exit(1)
    else:
        logging.info('SMTP login success')
        return True

def send(target, title, content, adapter_name):
    global session
    corpo = MIMEText(content.encode('utf-8'), 'html', 'utf-8')
    corpo['From'] = target
    corpo['To'] = target
    corpo['Subject'] = Header(title, 'utf-8')
    session.sendmail(target, [target], corpo.as_string())
    logging.info('Sent an email by %s', adapter_name)
    # delay
    sleep(1)