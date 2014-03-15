#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import BASE, CONF, CONSUMER_KEY, CONSUMER_SECRET, APP_NAME
from commands import Executor
from commands.repository import registered_commands
from json import load
from twitter_helpers import TwitterClient
from os import path
import logging
import modules.twitter_api as twitter
import sys
import signal


def main():

    def signal_handler(signal_num, stack_frame):
        try:
            stream.close()
        except Exception as ex:
            print "EXCEPTION ON SIGNAL %i " % signal_num
            print ex

        logging.info('Signal %i caught, %s is exiting' % (signal_num, APP_NAME))

    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    signal.signal(signal.SIGPWR, signal_handler)

    # configure error logging
    logging.basicConfig(filename=path.join(BASE, 'hawkeye.log'), level=logging.INFO,
                        format='%(asctime)s [%(levelname)s]: %(message)s')

    logging.info('%s is starting' % APP_NAME)

    # retrieve configuration
    try:
        with open(CONF, 'r') as conf_file:
            full_config = load(conf_file)
            app_config = full_config['hawkeye']
    except KeyError as e:
        logging.critical('Missing configuration section: %s' % str(e))
        logging.info('%s is exiting' % APP_NAME)
        exit(1)
    except IOError as e:
        logging.critical('Error trying to read configuration file: %s' % str(e))
        logging.info('%s is exiting' % APP_NAME)
        exit(1)

    if 'plugin_directories' in app_config:
        logging.info('Importing plugins')
        try:
            commands_names = [command[0] for command in registered_commands]

            from importlib import import_module

            for folder, packages in app_config['plugin_directories'].iteritems():
                sys.path.append(path.abspath(path.expanduser(folder)))

                for package in packages:
                    try:
                        module = import_module('%s.repository' % package)
                        module_commands = module.registered_commands
                        logging.info('\tLoading commands from %s ' % module.__name__)

                        # we can only import commands for which the command name hasn't already been registered yet
                        registrable = [command for command in module_commands if command[0] not in commands_names]
                        non_registrable = [command for command in module_commands if command[0] in commands_names]

                        for not_registered in non_registrable:
                            logging.error('\t\t%s command won\'t be registered, command name is already used.'
                                          % not_registered[0])

                        registered_commands.extend(registrable)

                        for registered in registrable:
                            commands_names.append(registered[0])

                    except ImportError as e:
                        logging.error('\tImportError ' % str(e))

        except KeyError:
            pass

        logging.info('Plugins import finished')

    try:
        exclusive = (app_config['command_registering_strategy'] == '-')
    except KeyError:
        exclusive = False

    if exclusive:
        # keep only the non-listed commands
        commands = [registered for registered in registered_commands if registered[0] not in app_config['commands']]
    else:
        # only keep the listed commands
        commands = [registered for registered in registered_commands if registered[0] in app_config['commands']]

    Executor.allowed = [command[0] for command in commands]
    Executor.disallowed = [command[0] for command in registered_commands if command not in commands]

    # register all commands
    for command in commands:
        logging.info('Registering %s command' % command[0])
        Executor.commands.register(command[0], command[1])

    # configure twitter clients (stream + classic)
    auth = twitter.OAuth(app_config['oauth_token'], app_config['oauth_token_secret'], CONSUMER_KEY, CONSUMER_SECRET)
    stream = twitter.TwitterStream(api_version=1.1, domain='userstream.twitter.com', auth=auth).user()

    client = TwitterClient(auth=auth)
    Executor.client_settings = client.account.settings()
    Executor.set_client(client)

    # tweet processing, main loop
    for t in stream:

        # we only want tweets or DMs
        if t.get('direct_message') or t.get('text'):

            sender = 'user'

            # direct message
            if t.get('direct_message'):
                tweet = t['direct_message']
                sender = 'sender'
            # tweet
            else:
                tweet = t
                tweet['sender_screen_name'] = tweet['user']['screen_name']
                # we want to make sure the tweet is directly addressed to Hawkeye

                if not tweet['text'].startswith('@%s ' % Executor.client_settings['screen_name']):
                    continue

            # only process tweets/DMs from whitelisted users
            if tweet[sender]['screen_name'] in app_config['whitelist']:

                # the command name is the first hastag
                if len(tweet['entities']['hashtags']) > 0:
                    command = tweet['entities']['hashtags'][0]['text']
                    # del tweet['entities']['hashtags'][0]

                    if command in Executor.allowed:
                        executor = Executor()
                        try:
                            options = full_config[command]
                        except KeyError:
                            options = None

                        # load the command w/ its options
                        executor.load(command, options)
                        # launch the command !
                        executor.process(tweet)
                    else:
                        if command in Executor.disallowed:
                            logging.warning('Denied command attempted: %s ' % (tweet['text']))

    return

if __name__ == '__main__':
    main()
