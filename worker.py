#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import CONF, CONSUMER_KEY, CONSUMER_SECRET, APP_NAME
from commands import Executor
from commands.repository import registered_commands
from json import load
import logging
import modules.twitter_api as twitter


def main():

    # configure error logging
    logging.basicConfig(filename="./hawkeye.log", level=logging.INFO,
                        format='%(asctime)s [%(levelname)s]: %(message)s')

    # retrieve configuration
    try:
        with open(CONF, 'r') as conf_file:
            full_config = load(conf_file)
            app_config = full_config['hawkeye']
    except KeyError as e:
        logging.critical('Missing configuration section: %s' % str(e))
        exit(1)
    except IOError as e:
        logging.critical('Error trying to read configuration file: %s' % str(e))
        exit(1)

    # register all commands
    for command in registered_commands:
        logging.info("Registering %s command" % command[0])
        Executor.commands.register(command[0], command[1])

    logging.info("%s's started" % APP_NAME)

    # configure twitter clients (stream + classic)
    auth = twitter.OAuth(app_config['oauth_token'], app_config['oauth_token_secret'], CONSUMER_KEY, CONSUMER_SECRET)
    client = twitter.Twitter(auth=auth)
    stream = twitter.TwitterStream(api_version=1.1, domain='userstream.twitter.com', auth=auth).user()

    # tweet processing, main loop
    for t in stream:

        # we only want tweets or DMs that are from whitelisted users
        if t.get('direct_message') or t.get('text'):

            sender = 'user'
            if t.get('direct_message'):
                tweet = t['direct_message']
                sender = 'sender'
            else:
                tweet = t

            if tweet[sender]['screen_name'] in app_config['whitelist']:

                # the command name is the first hastag, or the default one if no hastags
                if len(tweet['entities']['hashtags']) == 0:
                    command_name = app_config["default_command"]
                else:
                    command_name = tweet['entities']['hashtags'][0]['text']
                    del tweet['entities']['hashtags'][0]

                try:
                    command_options = full_config[command_name]
                except KeyError:
                    command_options = []

                executor = Executor()

                try:
                    # load the command w/ its options
                    executor.load(command_name, command_options)
                except AttributeError:
                    continue

                # launch the command !
                executor.process(tweet, client)

    return

if __name__ == '__main__':
    main()
