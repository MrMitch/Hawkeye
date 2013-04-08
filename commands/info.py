# -*- coding: utf-8 -*-
from datetime import timedelta
from commands import Command, Executor
import logging
import twitter_helpers

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


class Stats(Command):

    def execute(self, tweet):
        stats = []
        try:
            with open("/proc/uptime", 'r') as u:
                stats.append(('uptime', str(timedelta(seconds=float(u.readline().split()[0])))))
        except IOError:
            pass

        try:
            with open("/proc/loadavg", 'r') as l:
                stats.append(('load', ', '.join(l.readline().split()[0:3])))
        except IOError:
            pass

        try:
            with open("/proc/meminfo", 'r') as m:
                lines = [l.split()[:2] for l in m.readlines()]

            for info in lines:
                if info[0] in ['MemTotal:', 'MemFree:', 'SwapTotal:', 'SwapFree:']:
                    stats.append((info[0].replace(':', ''), '%.3f Go' % (float(info[1]) / 1048576)))
        except IOError:
            pass

        if len(tweet['entities']['hashtags']) > 1:
            hashtags = [h['text'] for h in tweet['entities']['hashtags']]

            if 'ip' in hashtags:

                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 9))
                    stats.append(('ip', s.getsockname()[0]))
                    s.close()
                except (socket.error, socket.herror, socket.gaierror, socket.herror, socket.sslerror):
                    pass

            if 'traffic' in hashtags or 'process' in hashtags or 'processes' in hashtags:
                import re

                if 'traffic' in hashtags:
                    try:
                        with open("/proc/net/dev", 'r') as d:
                            lines = [l.split() for l in d.readlines()]

                        regex = re.compile(r'^(eth|wlan)')
                        interfaces = [[i[0], float(i[1]), float(i[len(i) - 1])]
                                      for i in lines if regex.match(i[0]) is not None]

                        for i in interfaces:
                            stats.append((i[0].replace(':', ''),
                                          "Down: %.3f Go, Up: %.3f Go" % (i[1] / 1073741824, i[2] / 1073741824)))
                    except IOError:
                        pass

                if 'process' in hashtags or 'processes' in hashtags:
                    from os import walk
                    try:
                        regex = re.compile(r'^[0-9]+$')
                        stats.append(('processes', len([dir for dir in walk('/proc', followlinks=False).next()[1]
                                                        if regex.match(dir)])))
                    except StopIteration:
                        pass

        # import json
        # print json.dumps(stats, indent=4, separators=(', ', ': '))
        return stats

    def post_hook(self, stats, tweet):
        return '\n'.join([': '.join((s[0], str(s[1]))) for s in stats]), twitter_helpers.DIRECT_MESSAGE


class List(Command):

    def execute(self, tweet):
        if Executor.allowed is not None:
            return Executor.allowed
        return []

    def post_hook(self, result, tweet):
        return ', '.join(result),