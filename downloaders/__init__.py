from urllib import unquote
from urlparse import urlparse


class FileDownloader(object):

    def __init__(self, options=None):
        super(FileDownloader, self).__init__()
        self.parse_options(options)

    def parse_options(self, options):
        pass

    def download(self, url, output_directory, filename=None):
        pass

    def extract_filename(self, url):
        return unquote(urlparse(url).path.split('/')[-1])