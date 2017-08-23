from telegram.ext import Updater, CommandHandler, Job

def start(bot, update):
    if update.message.chat.id == "-231093383":
        update.message.reply_text("{}".format(id))
    else:
        update.message.reply_text("Sosite!")

def hello(bot, update):
    if update.message.chat.id == "-231093383":
        update.message.reply_text(
            'Hello {}'.format(update.message.from_user.first_name))
    else:
        update.message.reply_text("Sosite!")

def callback_minute(bot, job):
    bot.send_message(chat_id='-231093383',
                     text='Sosite!')

updater = Updater('')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))

queue = updater.job_queue

queue.run_repeating(callback_minute, 60.0)

updater.start_polling()
updater.idle()
