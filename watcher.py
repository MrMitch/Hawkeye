#!/usr/bin/env python
# -*- coding: utf-8 -*-

import twitter
from config import CONSUMER_SECRET, CONSUMER_KEY, CONF, write_configuration_file
from json import load


def main():
    try:
        with open(CONF, 'r') as conf:
            obj = load(conf)
            oauth_token = obj['oauth']['token']
            oauth_token_secret = obj['oauth']['token_secret']
    except BaseException as e:
        print e
        try:
            print 'unallowed'
            write_configuration_file()
        except BaseException as e:
            exit('Unable to write configuration file')

    print oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET

    auth = twitter.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)

    stream = twitter.TwitterStream(api_version=1.1, domain='userstream.twitter.com', auth=auth).user()
    for t in stream:
        print t
        if t.get('text'):
            print t['text']

if __name__ == '__main__':
    main()