from commands.download import HTTPDownload, RealDebridDownload

registered_commands = [
    ['dl', HTTPDownload],
    ['rd', RealDebridDownload]
]