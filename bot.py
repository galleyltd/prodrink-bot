from telegram.ext import Updater, CommandHandler, Job
from github import Github

import datetime

prodrink = Github("").get_organization("prodrink")

chatid = -1

one_hour = datetime.timedelta(hours=1)

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
    for e in prodrink.get_events():
        if e.created_at > last_hour:
            bot.send_message(chat_id='-',
                             text="{} for repo {} from {}".format(e.type, e.repo.name, e.actor.name))

updater = Updater('')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))

queue = updater.job_queue

queue.run_repeating(callback_minute, 60.0*60.0, first=0)

updater.start_polling()
updater.idle()
