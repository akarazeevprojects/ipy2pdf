#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import subprocess
import telegram
import logging
import json
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_token():
    with open('token.json') as jsn:
        data = json.load(jsn)
    return data['token']


def text_handler(bot, update):
    update.message.reply_text("Better send me a file with .ipynb extension")


def converter(bot, update):
    file_path = None

    chat_dir = os.path.join("data", str(update.message.chat_id))

    if not os.path.exists(chat_dir):
        os.mkdir(chat_dir)

    if update.message.document is not None:
        # Document case
        file_name = update.message.document.file_name

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


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(get_token())
    bot = telegram.Bot(token=get_token())
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.document, converter))
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
