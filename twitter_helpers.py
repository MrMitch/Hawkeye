# -*- coding: utf-8 -*-
import logging
from textwrap import TextWrapper
import modules.twitter_api as t

TWEET = 0
DIRECT_MESSAGE = 1


class TwitterClient(t.Twitter):

    def __init__(
            self, format="json",
            domain="api.twitter.com", secure=True, auth=None,
            api_version=1.1):
        super(TwitterClient, self).__init__(format=format, domain=domain, secure=secure,
                                            auth=auth, api_version=api_version)

    def respond(self, question, response):
        username = question['sender_screen_name']

        # if a response type is specified, use this response type
        if type(response) == tuple:
            response_type = DIRECT_MESSAGE if response[1] == DIRECT_MESSAGE else TWEET
        else:
            # by default, the response type is the same as the question's type
            # i.e respond to a tweet by a tweet and to a DM by a DM
            response_type = DIRECT_MESSAGE if 'direct_message' in question else TWEET

        if response_type == DIRECT_MESSAGE:
            w = TextWrapper(width=140, break_long_words=False, replace_whitespace=False)
            for l in w.wrap(response[0]):
                try:
                    self.direct_messages.new(user=username, text=l)
                except t.TwitterHTTPError as e:
                    logging.error('Error sending response DM: %s' % e)
        else:
            w = TextWrapper(width=140 - (len(username) + 2), break_long_words=False, replace_whitespace=False)
            for l in w.wrap(response[0]):
                kw = {"status": '@%s %s' % (username, unicode(l))}
                if question.get('user', None) is not None:
                    kw['in_reply_to_status_id'] = question['id_str']

                try:
                    self.statuses.update(**kw)
                except t.TwitterHTTPError as e:
                    logging.error('Error sending response tweet: %s' % e)
