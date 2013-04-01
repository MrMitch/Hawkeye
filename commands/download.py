from commands import Command
from datetime import datetime
from downloaders.http import RealDebridFileDownloader, HTTPFileDownloader


class HTTPDownload(Command):

    def __init__(self, options):
        super(HTTPDownload, self).__init__(options)
        self.output_dir = options['output_dir']
        self.downloader = HTTPFileDownloader()
        self.pre_hook = self.pre
        self.post_hook = self.post

    def __notify(self, tweet, client, start=True):
        # datetime.strptime doesn't support %z, hence the +0000 in the string
        date = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if start:
            t = 'D'
        else:
            t = 'Done d'

        t += 'ownloading links sent on %s' % date.strftime('%Y/%m/%d %H:%M:%S')

        client.direct_messages.new(user=tweet['sender_screen_name'], text=t)

    def pre(self, tweet, client):
        self.__notify(tweet, client)

    def post(self, result, tweet, client):
        self.__notify(tweet, client, False)

    def execute(self, tweet):
        for url in tweet['entities']['urls']:
            self.downloader.download(url['expanded_url'], self.output_dir)


class RealDebridDownload(HTTPDownload):

    def __init__(self, options):
        super(RealDebridDownload, self).__init__(options)
        self.downloader = RealDebridFileDownloader(options)
