from FileDownloader import FileDownloader
from urllib2 import build_opener
from os import path


class HTTPFileDownloader(FileDownloader):

    def __init__(self):
        super(HTTPFileDownloader, self).__init__()

    def download(self, url, destination):
        fullpath = path.join(destination, 'test')
        try:
            opener = build_opener()
            stream = opener.open(url)

            with open(fullpath, 'wb') as output:
                while True:
                    try:
                        content = stream.read(10240)  # 10 KB

                        if not content:
                            break

                        output.write(content)
                    except KeyboardInterrupt:
                        break

                stream.close()

        except BaseException as e:
            print str(e)

    def parse_options(self, options):
        pass
