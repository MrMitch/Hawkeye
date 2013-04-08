from commands.download import HTTPDownload, RealDebridDownload
from commands.info import Log, Stats, List


registered_commands = [
    ['dl', HTTPDownload],
    ['rd', RealDebridDownload],
    ['commands', List],
    ['stats', Stats],
    ['log', Log]
]