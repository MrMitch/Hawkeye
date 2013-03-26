from FileDownloader import FileDownloader
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