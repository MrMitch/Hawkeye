from HTTPFileDownloader import HTTPFileDownloader
from rdcli import RDWorker, LoginError


class RealDebridFileDownloader(HTTPFileDownloader):

    def __init__(self):
        super(RealDebridFileDownloader, self).__init__()

    def __download(self, url, destination):
        return HTTPFileDownloader.download(self, url, destination)

    def download(self, url, destination):
        link = self.rd_worker.unrestrict(url)
        print "RealDebridFileDownloader"
        return self.__download(link, destination)

    def parse_options(self, options):
        self.rd_worker = RDWorker(options['cookie_file'])

        try:
            self.rd_worker.login(options['username'], options['password'])
        except LoginError as e:
            print str(e)
