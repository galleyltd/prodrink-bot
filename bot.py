from telegram.ext import Updater, CommandHandler, Job
from github import Github

import datetime
import redis
import sys

chatid = -231093383

one_hour = datetime.timedelta(minutes = 4*60.0)

utc = datetime.timedelta(hours = 3)

def get(bot, update):
    if update.message.chat.id == chatid:
        update.message.reply_text(REDIS_QUEUE.get(update.message.text.replace('/get ', '')).decode())
    else:
        update.message.reply_text("Sosite!")

def set(bot, update):
    if update.message.chat.id == chatid:
        empty, key, value = update.message.text.replace('/set', '').split(' ')
        REDIS_QUEUE.set(key, value)
        update.message.reply_text("Setting for key {} value {}".format(key, value))
    else:
        update.message.reply_text("Sosite!")

def start(bot, update):
    if update.message.chat.id == chatid:
        update.message.reply_text("Hello, Prodrink chat!")
    else:
        update.message.reply_text("Sosite!")

def hello(bot, update):
    if update.message.chat.id == chatid:
        update.message.reply_text(
            'Hello {}'.format(update.message.from_user.first_name))
    else:
        update.message.reply_text("Sosite!")

def callback_minute(bot, job):
    last_hour = datetime.datetime.now() - one_hour
    print(last_hour)
    for e in prodrink.get_events():
        if e.created_at > last_hour:
            bot.send_message(chat_id='-231093383',
                             text="{} for repo {} from {} at {} MSK".format(e.type, e.repo.name, e.actor.name, e.created_at + utc))

def main(argv):
    if len(argv) != 3:
        print('Expected usage of script:')
        print('python3 bot.py redishost redispost redispassword')
        sys.exit(2)
    host, port, pwd = argv
    try:
        global REDIS_QUEUE
        REDIS_QUEUE = redis.StrictRedis(host=host, port=port, password=pwd)
    except Exception:
        print("Provided params are incorrect. Couldn't connect to Redis instance")

    global prodrink
    prodrink = Github("").get_organization("prodrink")

    updater = Updater('')

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('hello', hello))
    updater.dispatcher.add_handler(CommandHandler('get', get))
    updater.dispatcher.add_handler(CommandHandler('set', set))

    queue = updater.job_queue

    queue.run_repeating(callback_minute, interval=60.0 * 60.0, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main(sys.argv[1:])

