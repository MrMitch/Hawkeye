from HTTPFileDownloader import HTTPFileDownloader
from modules.rdcli import RDWorker, LoginError


class RealDebridFileDownloader(HTTPFileDownloader):

    def __init__(self, options):
        super(RealDebridFileDownloader, self).__init__(options)

    def download(self, url, output_directory, filename=None):
        link, _filename = self.rd_worker.unrestrict(url)

        if not filename:
            filename = _filename

        downloaded, headers = super(RealDebridFileDownloader, self).download(link, output_directory, filename)

        return downloaded

    def parse_options(self, options):
        self.rd_worker = RDWorker(options['cookie_file'])

        try:
            self.rd_worker.login(options['username'], options['password'])
        except LoginError as e:
            print str(e)
