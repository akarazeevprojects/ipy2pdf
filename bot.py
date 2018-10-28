from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import subprocess
import telegram
import json
import os
import re
import logging
import platform
import emoji
from utils import BotLogs

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DATA_FOLDER = "data"
PROXY_URL = None
if platform.system() == 'Darwin':
    PROXY_URL = 'socks5://127.0.0.1:9050'
elif platform.system() == 'Linux':
    PROXY_URL = 'socks5h://127.0.0.1:9050'

# botlogger = BotLogs("bot_logger", "bot.log")

help_text = list()
help_text.append("Этот бот позволяет конвертировать *.ipynb* в *.pdf* -- просто пришли мне *.ipynb* файл")
help_text.append('')
help_text.append("Команда /files выводит список файлов в твоей директории и позволяет скачать нужный файл")
help_text = '\n'.join(help_text)

start_text = list()
start_text.append("Привет!")
start_text.append(help_text)
start_text.append('')
start_text.append("Возможно, тебе также будет интересно подписаться на канал @akarazeevchannel")
start_text.append(emoji.emojize("Если возникнут трудности/будут пожелания или замечания, то направляй их пожалуйста @akarazeev :relieved:", use_aliases=True))
start_text = '\n'.join(start_text)

brackets_text = "Убери скобочки из названия файла, пожалуйста. И пришли заново"
emptyfolder_text = "Файлы отсутствуют. Пришли мне что-нибудь"


def get_token():
    with open("token.json") as jsn:
        data = json.load(jsn)
    return data["token"]


def converter(bot, update):
    # global botlogger
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

    users_number = len(os.listdir('data/'))

    update.message.reply_text(f"Конвертирую...\nПока ты ждёшь -- можешь почитать @akarazeevchannel :)\n\nСтатитика показывает, что примерное число активных пользователей: *{users_number}*", parse_mode=telegram.ParseMode.MARKDOWN)
    print(file_path)
    # bash_command = "source /home/anton/.envs/ipy/bin/activate && cd /home/anton/WD/ipy2pdf/ && python3 ipy2pdf '{}'".format(file_path)
    bash_command = "cd /home/anton/WD/ipy2pdf/ && python3 ipy2pdf '{}'".format(file_path)
    print(bash_command)
    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
    process.communicate()
    print("Converted!")

    pdf_path = file_path.replace(".ipynb", ".pdf")

    with open(pdf_path, 'rb') as f:
        update.message.reply_document(f)

    # botlogger.add_msg("user {} send {}".format(str(update.message.chat_id), file_name))

    # update.message.reply_text(make_info())


# def make_info():
#     global botlogger
#     reqs = str(botlogger.number_of_requests())
#     firstdate = botlogger.first_date()
#     msg = '{} requests since launch ({})'.format(reqs, firstdate)
#     return msg


# def info(bot, update):
#     msg = make_info()
#     update.message.reply_text(msg)


def get_chat_dir(chat_id):
    return os.path.join(DATA_FOLDER, str(chat_id))


def get_files_list(chat_dir):
    """Short summary.

    Args:
        chat_dir (str): Path to user's folder.

    Returns:
        list: List of pairs (number, filename)

    """
    print(chat_dir)
    chat_dir_list = os.listdir(chat_dir)
    chat_dir_list = sorted(list(filter(lambda x: not x.startswith('.'), chat_dir_list)))
    chat_dir_list = list(enumerate(chat_dir_list))
    return chat_dir_list


def files(bot, update):
    chat_dir = get_chat_dir(update.message.chat_id)

    try:
        if not os.path.exists(chat_dir):
            raise Exception

        chat_dir_list = get_files_list(chat_dir)

        if len(chat_dir_list) == 0:
            raise Exception

        response_text = list()
        response_text.append("Содержимое твоей папки:")
        for number, filename in chat_dir_list:
            response_text.append(f'- *{filename}* --скачать--> /{number}')
        response_text = '\n'.join(response_text)
        update.message.reply_text(response_text, parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text(emptyfolder_text)


def choose_file(bot, update):
    command = update.message.text
    chat_id = update.message.chat_id

    file_number = int(command[1:])
    chat_dir = get_chat_dir(chat_id)
    chat_dir_list = get_files_list(chat_dir)
    filename = chat_dir_list[file_number][1]

    update.message.reply_text(f'Ты просишь меня скачать файл *{filename}*, который имеет порядковый номер *{file_number}* в директории. Окей...', parse_mode=telegram.ParseMode.MARKDOWN)
    with open(os.path.join(get_chat_dir(chat_id), filename), 'rb') as f:
        update.message.reply_document(f)


def help(bot, update):
    update.message.reply_text(help_text, parse_mode=telegram.ParseMode.MARKDOWN)


def start(bot, update):
    update.message.reply_text(start_text, parse_mode=telegram.ParseMode.MARKDOWN)


def main():
    token = get_token()
    print('-> USE PROXY')
    req = telegram.utils.request.Request(proxy_url=PROXY_URL,
                                         read_timeout=30, connect_timeout=20,
                                         con_pool_size=10)
    bot = telegram.Bot(token=token, request=req)

    updater = Updater(bot=bot)
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(CommandHandler("files", files))
    # dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, help))
    dp.add_handler(MessageHandler(Filters.document, converter))
    dp.add_handler(MessageHandler(Filters.command, choose_file))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
