import coloredlogs
import logging
import re


class Logger():
    def __init__(self, name=__file__):
        if name.count('/') > 2:
            name = re.findall('\w+\/\w+\.\w+$', name)[0]
        elif name.count('/') == 1:
            name = re.findall('\w+.\w+$', name)[0]

        self.logger = logging.getLogger(name)
        coloredlogs.install(level='DEBUG')
        coloredlogs.install(level='DEBUG',
                            logger=self.logger,
                            fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s')

    def log(self, x):
        self.logger.debug(x)

    def debug(self, x):
        self.logger.debug(x)

    def info(self, x):
        self.logger.info(x)

    def warning(self, x):
        self.logger.warning(x)

    def error(self, x):
        self.logger.error(x)

    def critical(self, x):
        self.logger.critical(x)
