#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
try:
    import logging
    import traceback
except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))


class CustomFormatter(logging.Formatter):
    """ Logging Formatter to add colors and count warning / errors
    """
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s - %(levelname)s  > %(message)s (%(name)s:%(lineno)d)'
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Log(object):
    """Logging wrapper for better output
    """

    def __init__(self, name: str = 'applogger', prefix: str = '', level: int = 10, logDir: str = None):
        """Constructor application logger

        Args:
            name (str, optional): [description]. Defaults to 'applogger'.
            level (int, optional): [description]. Defaults to logging.DEBUG.
            enableLogFile (bool, optional): [description]. Defaults to False
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.loglevel = level
        self.logDir = logDir
        self.prefix = prefix

        if(logDir):
            # use log file
            fh = logging.FileHandler(self.logDir + '%s.log' % name, 'w')
            self.logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(CustomFormatter())
        self.logger.addHandler(sh)

        sys.excepthook = self.handle_excepthook

    def debug(self, msg):
        self.logger.debug("{}: {}".format(self.prefix, msg))

    def info(self, msg):
        self.logger.info("{}: {}".format(self.prefix, msg))

    def warning(self, msg):
        self.logger.warning("{}: {}".format(self.prefix, msg))

    def error(self, msg):
        self.logger.error("{}: {}".format(self.prefix, msg))

    def critical(self, msg):
        self.logger.critical("{}: {}".format(self.prefix, msg))

    def print(self, msg: str = ' ', end: str = '\r'):
        if(self.loglevel < 100):
            msg = ("{}:{}".format(self.prefix, msg))
            print(msg, end)

    def handle_excepthook(self, type, message, stack):
        self.logger.critical(f'{self.prefix}:An unhandled exception occured: {message}. Traceback: {traceback.format_tb(stack)}')
