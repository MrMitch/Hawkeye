from commands import Error
from commands.download import HTTPDownload, RealDebridDownload
from commands.log import Log


registered_commands = [
    ['dl', HTTPDownload],
    ['rd', RealDebridDownload],
    ['log', Log]
    #, ['error', Error]
]