# -*- coding: utf-8 -*-
from textwrap import TextWrapper
import modules.twitter_api

TWEET = 0
DIRECT_MESSAGE = 1


class TwitterClient(modules.twitter_api.Twitter):

    def __init__(
            self, format="json",
            domain="api.twitter.com", secure=True, auth=None,
            api_version=1.1):
        super(TwitterClient, self).__init__(format=format, domain=domain, secure=secure,
                                            auth=auth, api_version=api_version)

    def respond(self, question, response):
        username = question['sender_screen_name']

        response_type = TWEET
        if len(response) > 1 and response[1] == DIRECT_MESSAGE:
            response_type = DIRECT_MESSAGE

        if response_type == DIRECT_MESSAGE:
            w = TextWrapper(width=140, break_long_words=False, replace_whitespace=False)
            for l in w.wrap(response[0]):
                self.direct_messages.new(user=username, text=l)
        else:
            w = TextWrapper(width=140 - (len(username) + 2), break_long_words=False, replace_whitespace=False)
            for l in w.wrap(response[0]):
                kw = {"status": '@%s %s' % (username, unicode(l))}
                if hasattr(question, 'user'):
                    kw['in_reply_to_status_id'] = question['id_str']

                self.statuses.update(**kw)
