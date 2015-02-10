# -*- coding: utf-8 -*-
import logging
import smtplib
import sys
import eventlet
eventlet.monkey_patch()

from email.mime.text import MIMEText
from email.header import Header

session = None
connect_params = {}

def connect(server='smtp.gmail.com', port=587, user='', passwd='', tls=False):
    params = locals()
    global session, connect_params
    session = smtplib.SMTP(server, port)
    session.ehlo()
    if tls:
        session.starttls()
    try:
        result = session.login(user, passwd)
        # check smtp login status (235, 270 = accepted)
        if result[0] != 235 and result[0] != 270 and 'Accept' not in result[1]:
            raise Exception(
                'The connection to the SMTP server was unsuccessful.')
        # check smtp connection status
        status = session.noop()[0]
        if status != 250:
            raise Exception('The connection to the SMTP server was lost.')
    except:
        logging.error('Unable to logon to the SMTP server.')
        sys.exit(1)
    else:
        connect_params = params
        logging.info('Successfully connected to the SMTP server.')
        return True


def test_session():
    global session
    try:
        status = session.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False


def send(target, title, content, adapter_name):
    global session, connect_params
    if not test_session():
        connect(**connect_params)
    corpo = MIMEText(content.encode('utf-8'), 'html', 'utf-8')
    corpo['From'] = target
    corpo['To'] = target
    corpo['Subject'] = Header(title, 'utf-8')
    session.sendmail(target, [target], corpo.as_string())
    logging.info('The mail has been sent successfully originated from "%s".',
        adapter_name)
    # delay
    eventlet.sleep(0.5)
