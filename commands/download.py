from commands import Command
from datetime import datetime
from downloaders.http import RealDebridFileDownloader, HTTPFileDownloader
from os import path
import twitter_helpers

fullpath = lambda p: path.abspath(path.expanduser(p))


class HTTPDownload(Command):

    def __init__(self, options):
        super(HTTPDownload, self).__init__(options)
        self.output_dir = options['output_dir']
        self.downloader = HTTPFileDownloader()
        self.message = 'ownloading links sent on %s'

    def __notify(self, tweet, start=True):
        # datetime.strptime doesn't support %z, hence the +0000 in the string
        date = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if start:
            t = 'D'
        else:
            t = 'Done d'

        t += self.message % date.strftime('%Y/%m/%d %H:%M:%S')
        return t, twitter_helpers.DIRECT_MESSAGE

    def pre_hook(self, tweet):
        return self.__notify(tweet)

    def post_hook(self, result, tweet):
        return self.__notify(tweet, False)

    def execute(self, tweet):
        success = []
        for url in tweet['entities']['urls']:
            success.append(self.downloader.download(url['expanded_url'], self.output_dir))

        return success

    @classmethod
    def configurable_options(cls):
        return [
            ('output_dir', 'Folder where the files will be downloaded', fullpath)
        ]


class RealDebridDownload(HTTPDownload):

    def __init__(self, options):
        super(RealDebridDownload, self).__init__(options)
        self.downloader = RealDebridFileDownloader(options)
        self.message += ', using Real-Debrid'

    @classmethod
    def configurable_options(cls):
        from config import APP_NAME
        from hashlib import md5

        super_options = super(RealDebridDownload, cls).configurable_options()

        super_options.extend([
            ('cookie_file', 'The file were %s will store the RealDebrid cookie' % APP_NAME, fullpath),
            ('username', 'The username to use to login on RealDebrid', fullpath),
            ('password', 'The password to use to login on RealDebrid', lambda s: md5(s).hexdigest())
        ])

        return super_options