import socket
import time
import logging
import slackclient
import os
import sys

channel = os.environ['CHANNEL_ID']

def read_all(sock):
    eof = False
    time.sleep(0.2)
    s = b''
    while True:
        logging.debug('About to recv')
        try:
            r = sock.recv(4096)
            logging.debug("recv'd %s", repr(r))
        except BlockingIOError as e:
            logging.debug('Got BlockingIOError')
            break
        if len(r) == 0:
            eof = True
            break
        s += r
    s = s.decode()
    logging.info('Received from adventure: %s', repr(s))
    return (eof, s)

def send_to_adv(sock, s):
    logging.info('Sending to adventure: %s', repr(s))
    sock.sendall(s.encode())

def send_to_slack(sc, channel, message):
    sc.server.api_call('chat.postMessage',
        channel = channel,
        text = message,
        parse = 'full',
        username = 'Adventure Bot',
        as_user = 'false',
        icon_emoji = ':computer:')

logging.basicConfig(level = logging.INFO)
logging.info('Started')

logging.debug('Creating SlackClient')
sc = slackclient.SlackClient(os.environ['SLACK_TOKEN'])
logging.debug('Connecting to Slack')
if not sc.rtm_connect():
    logging.error('Connecting to Slack failed!')
    sys.exit(1)
logging.debug('Connected to Slack')

logging.debug('Connecting to adventure')
sock = socket.create_connection(('adventure', 3000))
sock.setblocking(0)

send_to_slack(sc, channel, 'Bot started. Only messages prefixed with `!` will be processed. Sending `!bounce` will restart the bot.')
(eof, s) = read_all(sock)
m = '```%s```' % (s,)
send_to_slack(sc, channel, m)

logging.info('Starting main loop')
while True:
    time.sleep(0.5)
    for m in sc.rtm_read():
        logging.debug(m)
        if m.get('type', None) == 'message' and m['text'].startswith('!') and m['channel'] == channel:
            if m['text'] == '!bounce':
                send_to_slack(sc, channel, 'Received !bounce; exiting')
                logging.info('Received !bounce; exiting')
                sys.exit(0)
            send_to_adv(sock, m['text'][1:] + '\n')
            (eof, s) = read_all(sock)
            r =  '```%s```' % (s,)
            send_to_slack(sc, channel, r)
            if eof:
                send_to_slack(sc, channel, 'Exiting due to EOF')
                logging.info('Exiting due to EOF')
                sys.exit(0)
