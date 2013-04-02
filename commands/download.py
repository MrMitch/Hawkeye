from commands import Command
from datetime import datetime
from downloaders.http import RealDebridFileDownloader, HTTPFileDownloader


class HTTPDownload(Command):

    def __init__(self, options):
        super(HTTPDownload, self).__init__(options)
        self.output_dir = options['output_dir']
        self.downloader = HTTPFileDownloader()
        self.message = 'ownloading links sent on %s'

    def __notify(self, tweet, client, start=True):
        # datetime.strptime doesn't support %z, hence the +0000 in the string
        date = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if start:
            t = 'D'
        else:
            t = 'Done d'

        t += self.message % date.strftime('%Y/%m/%d %H:%M:%S')

        client.direct_messages.new(user=tweet['sender_screen_name'], text=t)

    def pre_hook(self, tweet, client):
        self.__notify(tweet, client)

    def post_hook(self, result, tweet, client):
        self.__notify(tweet, client, False)

    def execute(self, tweet):
        success = []
        for url in tweet['entities']['urls']:
            success.append(self.downloader.download(url['expanded_url'], self.output_dir))

        return success


class RealDebridDownload(HTTPDownload):

    def __init__(self, options):
        super(RealDebridDownload, self).__init__(options)
        self.downloader = RealDebridFileDownloader(options)
        self.message += ', using Real-Debrid'
