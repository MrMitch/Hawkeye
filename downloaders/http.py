import logging
from downloaders import FileDownloader
from modules.rdcli import RDWorker, LoginError
from urllib import urlretrieve
from urllib2 import build_opener
from os import path


class HTTPFileDownloader(FileDownloader):

    def __init__(self, options=None):
        super(HTTPFileDownloader, self).__init__(options)

    def download(self, url, output_directory, filename=None):
        opener = build_opener()
        stream = opener.open(url)

        fullpath = path.abspath(path.expanduser(output_directory))

        if not filename:
            filename = self.extract_filename(stream.geturl())

        downloaded, headers = urlretrieve(url, path.join(fullpath, filename))

        return downloaded


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
            logging.error("Unable to initialize Real-Debrid worker: %s" % str(e))
