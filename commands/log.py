from commands import Command
import logging

levels = {
    'critical': logging.CRITICAL, 'debug': logging.DEBUG, 'error': logging.ERROR,
    'fatal': logging.FATAL, 'info': logging.INFO, 'warning': logging.WARNING
}


class Log(Command):

    def __init__(self, options):
        super(Log, self).__init__(options)

    def execute(self, tweet):
        try:
            level = levels[tweet['entities']['hashtags'][1]['text']]
        except (KeyError, IndexError):
            level = logging.INFO

        logging.log(msg="Log command: %s" % tweet['text'], level=level)