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


def main():

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

    try:
        optimist = (app_config['command_registering_strategy'] == '-')
    except KeyError:
        optimist = False

    if optimist:
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

    try:
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

                    # the command name is the first hastag, or the default one if no hastags
                    if len(tweet['entities']['hashtags']) == 0:
                        command = app_config["default_command"]
                        tweet['entities']['hashtags'].append({"indices": [0, 0], "text": command})
                    else:
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

    except KeyboardInterrupt:
        stream.close()
        logging.info('KeyboardInterrupt caught, %s is exiting' % APP_NAME)

    return

if __name__ == '__main__':
    main()
