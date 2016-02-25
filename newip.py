#! /usr/bin/env python

import logging
from os.path import isfile
from socket import gethostname
import requests

ip_url = 'https://api.ipify.org'
ip_file = 'ip'
my_host = gethostname()

## Import the config.py file
try:
    import config
    pb_api_key = config.pushbullet['access_token']
    twilio_account_sid = config.twilio['account_sid']
    twilio_auth_token = config.twilio['auth_token']
    twilio_ph = config.twilio['twilio_phone']
    mobile_ph = config.twilio['mobile_phone']
except ImportError:
    print "Rename config.py-sample to config.py"
    exit(1)

## Get the IP
try:
    my_ip = requests.get(ip_url, timeout=5).content.strip()
except requests.exceptions.ConnectionError:
    print "Connection timeout"
    exit(2)

## Pushbullet notifications
def pb_push(msg):
    if config.pushbullet['enable'] == 1:
        try:
            from pushbullet import Pushbullet
            pb = Pushbullet(pb_api_key)
            push = pb.push_note(my_host, msg)
        except ImportError:
            print "Install pushbullet.py library"
            exit(3)

## Twilio SMS
def twilio_sms(host, ip):
    try:
        if config.twilio['enable'] == 1:
            from twilio.rest import TwilioRestClient
            client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
            sms = client.messages.create(to = mobile_ph,
                                        from_ = twilio_ph,
                                        body = "Set IP: %s: %s" % (host, ip))
    except ImportError:
        print "Install twilio library"
        exit(4)

## Logging
log = logging.getLogger('newip.py')
log.setLevel(logging.INFO)
fh = logging.FileHandler('online.log')
fh.setLevel(logging.INFO)
frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        "%Y/%m/%d %H:%M:%S")
fh.setFormatter(frmt)
log.addHandler(fh)

## IP check, logging, and notifications
if isfile(ip_file):
    with open(ip_file, 'r') as old_ip:
        cur_ip = old_ip.read()
        if cur_ip != my_ip:
            with open(ip_file, 'w') as new_ip:
                new_ip.write(my_ip)
            status_msg = "IP address CHANGED -- %s" % my_ip
            log.info(status_msg)
            pb_push(status_msg)
            twilio_sms(my_host, my_ip)
else:
    with open(ip_file, 'w') as save_ip:
        save_ip.write(my_ip)
    status_msg = "IP address established -- %s" % my_ip
    log.info(status_msg)
    pb_push(status_msg)
    twilio_sms(my_host, my_ip)
