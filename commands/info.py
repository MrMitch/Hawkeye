# -*- coding: utf-8 -*-
from datetime import timedelta
from commands import Command, Executor
import logging
import utils

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
        stats = {}
        try:
            with open("/proc/uptime", 'r') as u:
                stats['uptime'] = str(timedelta(seconds=float(u.readline().split()[0])))
        except IOError:
            pass

        try:
            with open("/proc/loadavg", 'r') as l:
                stats['load'] = ', '.join(l.readline().split()[0:3])
        except IOError:
            pass

        try:
            with open("/proc/meminfo", 'r') as m:
                lines = [l.split()[:2] for l in m.readlines()]
            infos = ['%s %.3fGo' % (info[0], float(info[1]) / 1048576) for info in lines
                     if info[0] in ['MemTotal:', 'MemFree:', 'SwapTotal:', 'SwapFree:']]
            stats['RAM'] = ', '.join(infos)
        except IOError:
            pass

        if len(tweet['entities']['hashtags']) > 1:
            hashtags = [h['text'] for h in tweet['entities']['hashtags']]

            if 'ip' in hashtags:

                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 9))
                    stats['ip'] = s.getsockname()[0]
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
                        stats['traffic'] = ' ; '.join(["%s ▼: %.2f, ▲: %.2f" %
                                                       (i[0], i[1] / 1073741824, i[2] / 1073741824)
                                                       for i in interfaces])
                    except IOError:
                        pass

                if 'process' in hashtags or 'processes' in hashtags:
                    from os import walk
                    try:
                        regex = re.compile(r'^[0-9]+$')
                        stats['processes'] = len([dir for dir in walk('/proc', followlinks=False).next()[1]
                                                  if regex.match(dir)])
                    except StopIteration:
                        pass

        # import json
        # print json.dumps(stats, indent=4, separators=(', ', ': '))
        return stats

    def post_hook(self, stats, tweet):
        return '\n'.join(['='.join((name, str(value))) for name, value in stats.iteritems()]), utils.DIRECT_MESSAGE


class List(Command):

    def execute(self, tweet):
        if Executor.allowed is not None:
            return Executor.allowed
        return []

    def post_hook(self, result, tweet):
        return ', '.join(result),