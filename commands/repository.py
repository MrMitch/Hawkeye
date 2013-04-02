from commands import Error
from commands.download import HTTPDownload, RealDebridDownload


registered_commands = [
    ['dl', HTTPDownload],
    ['rd', RealDebridDownload],
    ['error', Error]
]