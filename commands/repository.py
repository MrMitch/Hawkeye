from commands import Error, List
from commands.download import HTTPDownload, RealDebridDownload
from commands.log import Log


registered_commands = [
    ['dl', HTTPDownload],
    ['rd', RealDebridDownload],
    ['commands', List],
    ['log', Log]
    #, ['error', Error]
]