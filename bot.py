#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import subprocess
import telegram
import json
import os
import re
import logging
from utils import BotLogs

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DATA_FOLDER = "data"

help_text = list()
help_text.append("Этот бот позволяет конвертировать .ipynb в .pdf -- просто пришли мне .ipynb файл.")
help_text.append("Команда /files выводит список файлов в твоей директории и позволяет скачать нужный файл")
help_text = '\n'.join(help_text)

start_text = list()
start_text.append("Привет!")
start_text.append(help_text)
start_text.append("Если возникнут трудности/будут пожелания или замечания, то направляй их пожалуйста @akarazeev :)")
start_text = '\n'.join(start_text)

brackets_text = "Убери скобочки из названия файла, пожалуйста. И пришли заново"
botlogger = BotLogs("bot_logger", "bot.log")


def get_token():
    with open("token.json") as jsn:
        data = json.load(jsn)
    return data["token"]


def converter(bot, update):
    global botlogger
    file_path = None

    chat_dir = os.path.join(DATA_FOLDER, str(update.message.chat_id))

    if not os.path.exists(chat_dir):
        os.mkdir(chat_dir)

    if update.message.document is not None:
        # Document case.
        file_name = update.message.document.file_name

        if re.compile(r'[\(\)\[\]]').search(file_name):
            update.message.reply_text(brackets_text)
            return

        if file_name[-6:].lower() != ".ipynb":
            update.message.reply_text(help_text)
            return

        file = bot.get_file(update.message.document.file_id)
        file_path = os.path.join(chat_dir, file_name)
        file.download(file_path)
    else:
        update.message.reply_text("Error")
        return

    file_path = os.path.realpath(file_path)

    update.message.reply_text("Converting...")
    print(file_path)
    bash_command = "ipy2pdf '{}'".format(file_path)
    print(bash_command)
    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
    process.communicate()
    print("Converted!")

    pdf_path = file_path.replace(".ipynb", ".pdf")

    with open(pdf_path, 'rb') as f:
        update.message.reply_document(f)

    botlogger.add_msg("user {} send {}".format(str(update.message.chat_id), file_name))

    # update.message.reply_text(make_info())


def make_info():
    global botlogger
    reqs = str(botlogger.number_of_requests())
    firstdate = botlogger.first_date()
    msg = '{} requests since launch ({})'.format(reqs, firstdate)
    return msg


def info(bot, update):
    msg = make_info()
    update.message.reply_text(msg)


def get_chat_dir(chat_id):
    return os.path.join(DATA_FOLDER, str(chat_id))


def get_files_list(chat_id):
    """Short summary.

    Args:
        chat_id (int):

    Returns:
        list: List of pairs (number, filename)

    """
    chat_dir = get_chat_dir(chat_id)
    chat_dir_list = os.listdir(chat_dir)
    chat_dir_list = sorted(list(filter(lambda x: not x.startswith('.'), chat_dir_list)))
    chat_dir_list = list(enumerate(chat_dir_list))
    return chat_dir_list


def files(bot, update):
    chat_dir_list = get_files_list(update.message.chat_id)
    print('Lol')

    response_text = list()
    response_text.append("Содержимое твоей папки:")
    for number, filename in chat_dir_list:
        response_text.append('- "{filename}" --скачать--> /{number}'.format(filename=filename, number=number))
    response_text = '\n'.join(response_text)
    update.message.reply_text(response_text)


def choose_file(bot, update):
    command = update.message.text
    chat_id = update.message.chat_id

    file_number = int(command[1:])
    chat_dir_list = get_files_list(chat_id)
    filename = chat_dir_list[file_number][1]

    update.message.reply_text('Ты просишь меня скачать файл "{filename}", который имеет порядковый номер {number} в директории. Окей...'.format(filename=filename, number=file_number))
    with open(os.path.join(get_chat_dir(chat_id), filename), 'rb') as f:
        update.message.reply_document(f)


def help(bot, update):
    update.message.reply_text(help_text)


def start(bot, update):
    update.message.reply_text(start_text)


def main():
    token = get_token()
    print('-> USE PROXY')
    req = telegram.utils.request.Request(proxy_url='socks5://127.0.0.1:9050',
                                         read_timeout=30, connect_timeout=20,
                                         con_pool_size=10)
    bot = telegram.Bot(token=token, request=req)

    updater = Updater(bot=bot)
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(CommandHandler("files", files))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, help))
    dp.add_handler(MessageHandler(Filters.document, converter))
    dp.add_handler(MessageHandler(Filters.command, choose_file))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
