#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from datetime import datetime
from time import sleep
import json
import os
import sys

import requests

from action import Action
from action_printer import ActionPrinter


DATE_FILE           = '.trello-to-zulip-date'
ZULIP_URL           = 'https://zulip.com/api/v1/messages'

parser = ArgumentParser(description='Read actions from Trello and post to Zulip')
parser.add_argument('-a', '--all',      action='store_true',                help='read all available actions')
parser.add_argument('-n', '--no-post',  action='store_true',                help='do not post messages')
parser.add_argument('-o', '--once',     action='store_true',                help='read actions once and exit')
parser.add_argument('-v', '--verbose',  action='store_true',                help='verbose progress output')
parser.add_argument('-c', '--config',   metavar='C', type=FileType('r'),    help='file to load settings (ENV takes priority)') 
parser.add_argument('-s', '--sleep',    metavar='S', type=int, default=60,  help='seconds to sleep between reading (default: 60)')
parser.add_argument('file',             type=FileType('r'), nargs='*',      help='read from file(s) instead of Trello')

ARGS = parser.parse_args()


def stderr(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')


class Logger(object):
    def _log(self, msg):
        if ARGS.verbose:
            # Defensive replace as this is a verbose/debug print only
            print msg.encode('utf-8', 'backslashreplace')

    def trello_json(self, msg):
        self._log(msg)

    def zulip_msg(self, msg):
        self._log(msg)

    def start_date(self, msg):
        self._log(msg)


class Config(object):
    def __init__(self):
        self.params = {}
        primary = os.environ
        secondary = {}
        if ARGS.config:
            secondary = json.loads(ARGS.config.read())
            ARGS.config.close()
        settings = ['TRELLO_KEY', 'TRELLO_BOARD_IDS', 'TRELLO_TOKEN', 'TRELLO_ORG', 'ZULIP_EMAIL', 'ZULIP_KEY', 'ZULIP_STREAM']
        for s in settings:
            if s in primary:
                self.params[s] = primary[s]
            elif s in secondary:
                self.params[s] = secondary[s]
            else:
                stderr("Setting not present in config: %s" % (s,))
                sys.exit(1)
    #
    # Config parameters
    #
    def trello_key(self):
        return self.params['TRELLO_KEY']
    def trello_board_ids(self):
        return self.params['TRELLO_BOARD_IDS']
    def trello_token(self):
        return self.params['TRELLO_TOKEN']
    def trello_org(self):
        return self.params['TRELLO_ORG']
    def zulip_email(self):
        return self.params['ZULIP_EMAIL']
    def zulip_key(self):
        return self.params['ZULIP_KEY']
    def zulip_stream(self):
        return self.params['ZULIP_STREAM']
    #
    # Derived
    #
    def trello_url(self):
        return 'https://api.trello.com/1/organization/%s' % (self.trello_org(),)
    def zulip_auth(self):
        return (self.zulip_email(), self.zulip_key())


class Loader(object):
    def __init__(self, logger):
        self.logger = logger
        self.last_date = None

    def _load_date(self):
        date = datetime.utcnow().isoformat() + 'Z'
        try:
            with open(DATE_FILE) as f:
                date = f.read()
        except IOError:
            pass
        return date

    def _save_date(self, date_str):
        if not ARGS.no_post:
            self.last_date = date_str
            with open(DATE_FILE, 'w') as f:
                f.write(date_str)

    def _from_files(self):
        for f in ARGS.file:
            text = f.read()
            if type(text) != unicode:
                text = text.decode('utf-8')
            f.close()
            yield text

    def _from_trello(self):
        post_params = {
            'key' : CONFIG.trello_key(),
            'token' : CONFIG.trello_token(),
            'actions' : 'all',
            'actions_limit' : '1000',
            'fields' : 'none',
            'boards' : 'organization',
            'board_fields' : 'name',
            'board_actions' : 'all',
            'board_actions_limit' : '1000',
            'board_actions_since' : None # Replaced each iteration
        }
        if ARGS.all:
            self.last_date = '1970-01-01T00:00:00Z'
            self.logger.start_date('Loading all available actions')
        else:
            self.last_date = self._load_date()
            self.logger.start_date('Loading actions since %s' % (self.last_date,))
        first = True
        while first or (not ARGS.once):
            if not first:
                try:
                    sleep(ARGS.sleep)
                except KeyboardInterrupt:
                    # Silence stack trace
                    print ''
                    sys.exit(0)
            else:
                first = False
            if self.last_date is not None:
                post_params['board_actions_since'] = self.last_date
            r = requests.get(CONFIG.trello_url(), params=post_params)
            if r.status_code == 200:
                text = r.text
                if type(text) != unicode:
                    text = r.text.decode('utf-8')
                yield text
            else:
                stderr('Error making Trello request: %d %s' % (r.status_code, r.text))

    def load_func(self):
        if ARGS.file:
            func = self._from_files
        else:
            func = self._from_trello
        for i in func():
            yield i

    def saw_action(self, action):
        if not ARGS.file:
            self.last_date = action.date()
            self._save_date(self.last_date)


class Runner(object):
    def __init__(self, logger):
        self.logger = logger

    def run(self):
        printer = ActionPrinter()
        loader = Loader(self.logger)
        for json_text in loader.load_func():
            self.logger.trello_json(json_text)
            json_dict = json.loads(json_text)
            actions = []
            if 'boards' in json_dict:
                boards = json_dict['boards']
                for b in boards:
                    if b['id'] in CONFIG.trello_board_ids():
                        actions += b['actions']
            elif 'actions' in json_dict:
                actions += json_dict['actions']
            else:
                stderr('Unknown input format')
                sys.exit(1)
            actions.sort(lambda x,y: cmp(x['date'], y['date']))
            for a in actions:
                action = Action(a)
                loader.saw_action(action)
                msg = printer.get_message(action)
                if msg is None:
                    continue
                self.logger.zulip_msg(msg.replace('\n', '\t'))
                post_params = {
                    'type' : 'stream',
                    'to' : CONFIG.zulip_stream(),
                    'subject' : action.derive_subject(),
                    'content' : msg
                }
                if not ARGS.no_post:
                    r = requests.post(ZULIP_URL, auth=CONFIG.zulip_auth(), data=post_params)
                    if r.status_code != 200:
                        stderr('Error %d POSTing to Zulip: %s' % (r.status_code, r.text))
            sys.stdout.flush()


if __name__ == '__main__':
    CONFIG = Config()
    logger = Logger()
    runner = Runner(logger)
    runner.run()

