# -*- coding: utf-8 -*-

import logging
from datetime import datetime as dd


class BotLogs:
    def __init__(self, logname, filename):
        # create logger with 'spam_application'
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(logging.DEBUG)

        self.filename = filename

        # Create file handler which logs even debug messages.
        fh = logging.FileHandler(self.filename)
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        fh.setFormatter(formatter)

        # Add the handlers to the logger.
        self.logger.addHandler(fh)

    def add_msg(self, msg):
        self.logger.info(msg)

    def number_of_requests(self):
        return len(self._load_logs())

    def first_date(self):
        logs = self._load_logs()
        dates = list(map(lambda x: x.split('--')[0].split()[0], logs))
        dates = list(map(lambda x: dd.strptime(x, '%Y-%m-%d'), dates))
        return sorted(dates)[0].strftime("%b %d, %Y")

    def _load_logs(self):
        with open(self.filename, 'r') as file:
            logs = file.readlines()
        return logs
