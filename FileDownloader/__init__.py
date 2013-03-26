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


class DownloaderFactory:
    """
    http://code.activestate.com/recipes/86900/
    """
    def register(self, methodName, constructor, *args, **kargs):
        """register a constructor"""
        _args = [constructor]
        _args.extend(args)
        setattr(self, methodName, Functor(*_args, **kargs))

    def get(self, downloader, *args, **kargs):
        return getattr(self, downloader)(*args, **kargs)

    def unregister(self, methodName):
        """unregister a constructor"""
        delattr(self, methodName)


class Functor:

    def __init__(self, function, *args, **kargs):
        assert callable(function), "function should be a callable obj"
        self._function = function
        self._args = args
        self._kargs = kargs

    def __call__(self, *args, **kargs):
        """call function"""
        _args = list(self._args)
        _args.extend(args)
        _kargs = self._kargs.copy()
        _kargs.update(kargs)
        return self._function(*_args, **_kargs)

downloader_factory = DownloaderFactory()