#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import subprocess
import telegram
import logging
import json
import os
import pickle
from datetime import datetime


class BotLogs:
    def __init__(self, logname, filename):
        # create logger with 'spam_application'
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(logging.DEBUG)

        self.filename = filename

        # create file handler which logs even debug messages
        fh = logging.FileHandler(self.filename)
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        fh.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(fh)

    def add_msg(self, msg):
        self.logger.info(msg)

    def number_of_requests(self):
        return len(self._load_logs())

    def first_date(self):
        logs = self._load_logs()
        dates = list(map(lambda x: x.split('--')[0].split()[0], logs))
        dates = list(map(lambda x: datetime.strptime(x, '%Y-%m-%d'), dates))
        return sorted(dates)[0].strftime("%b %d, %Y")

    def _load_logs(self):
        with open(self.filename, 'r') as file:
            logs = file.readlines()
        return logs


botlogger = BotLogs('bot_logger', 'bot.log')


def get_token():
    with open('token.json') as jsn:
        data = json.load(jsn)
    return data['token']


def text_handler(bot, update):
    update.message.reply_text("Better send me a file with .ipynb extension")


def converter(bot, update):
    global botlogger
    file_path = None

    chat_dir = os.path.join("data", str(update.message.chat_id))

    if not os.path.exists(chat_dir):
        os.mkdir(chat_dir)

    if update.message.document is not None:
        # Document case
        file_name = update.message.document.file_name

        if '(' or ')' or '[' or ']' in file_name:
            update.message.reply_text("Remove brackets from filename")
            return

        if file_name[-6:].lower() != ".ipynb":
            update.message.reply_text("Better send me a file with .ipynb extension")
            return

        file = bot.get_file(update.message.document.file_id)
        file_path = os.path.join(chat_dir, file_name)
        file.download(file_path)
    else:
        update.message.reply_text("Error")
        return

    file_path = os.path.realpath(file_path)

    update.message.reply_text("Converting ...")
    print(file_path)
    bash_command = "ipy2pdf '{}'".format(file_path)
    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
    process.communicate()
    print('Converted!')

    pdf_path = file_path.replace(".ipynb", ".pdf")

    with open(pdf_path, 'rb') as f:
        update.message.reply_document(f)

    update.message.reply_text(make_info())

    botlogger.add_msg("user {} send {}".format(str(update.message.chat_id), file_name))


def make_info():
    global botlogger
    reqs = str(39 + tmp.number_of_requests())
    firstdate = botlogger.first_date()
    msg = '{} requests since launch ({})'.format(reqs, firstdate)
    return msg


def info(bot, update):
    msg = make_info()
    update.message.reply_text(msg)


def main():
    updater = Updater(get_token())
    bot = telegram.Bot(token=get_token())
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.document, converter))
    dp.add_handler(MessageHandler(Filters.text, text_handler))
    dp.add_handler(CommandHandler("info", info))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
