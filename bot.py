from telegram.ext import Updater, CommandHandler, Job
from github import Github

import datetime
import redis
import sys

chatid = -231093383

one_minute = datetime.timedelta(minutes=5.0)


def delete(bot, update):
    if update.message.chat.id == chatid:
        empty, key = update.message.text.replace('/delete', '').split(' ')
        value = REDIS_QUEUE.get(key)
        if value is None:
            update.message.reply_text("There is nothing to delete for key: {}".format(key))
        else:
            update.message.reply_text("Deleting value for key {}".format(key))
            REDIS_QUEUE.delete(key)
    else:
        update.message.reply_text("Sosite!")


def getall(bot, update):
    if update.message.chat.id == chatid:
        res = []
        for key in REDIS_QUEUE.scan_iter():
            res.append("> {} = {}".format(key.decode(), REDIS_QUEUE.get(key).decode()))
        update.message.reply_text('\n'.join(res))
    else:
        update.message.reply_text("Sosite!")


def scan(bot, update):
    if update.message.chat.id == chatid:
        namespace = update.message.text.replace('/scan ', '')
        res = []
        for key in REDIS_QUEUE.scan_iter():
            if key.decode().find(namespace) >= 0:
                res.append("> {} = {}".format(key.decode(), REDIS_QUEUE.get(key).decode()))
        update.message.reply_text('\n'.join(res))
    else:
        update.message.reply_text("Sosite!")


def get(bot, update):
    if update.message.chat.id == chatid:
        key = update.message.text.replace('/get ', '')
        value = REDIS_QUEUE.get(key)
        if value is None:
            update.message.reply_text("No value for key: {}".format(key))
        else:
            update.message.reply_text(value.decode())
    else:
        update.message.reply_text("Sosite!")


def set(bot, update):
    if update.message.chat.id == chatid:
        empty, key, value = update.message.text.replace('/set', '').split(' ')
        REDIS_QUEUE.set(key, value)
        update.message.reply_text("Setting for key {} value {}".format(key, value))
    else:
        update.message.reply_text("Sosite!")


def help(bot, update):
    if update.message.chat.id == chatid:
        bot.send_message(chat_id=chatid,
                         text="""
        <b>Prodrink Bot Commands:</b>
        
        /get key - get value for key in Redis
        /getall - get all key, value pairs
        /scan namespace - get all values for namespace:*
        /set key value - set value for key in Redis
        /delete key - delete value for key in Redis
        /help - show this help
        """, parse_mode='HTML')
    else:
        update.message.reply_text("Sosite!")


def callback_minute(bot, job):
    last_minute = datetime.datetime.utcnow() - one_minute
    for e in prodrink.get_events():
        if e.created_at > last_minute:
            if e.type == 'PushEvent':
                print('not supported')
            elif e.type == 'IssuesEvent':
                bot.send_message(chat_id=chatid, text="""
                <a href="{}">{}</a> issue was created by {} in repo {} at {} UTC
                """.format(
                    e.payload.get('issue').get('html_url'),
                    e.payload.get('issue').get('title'),
                    e.payload.get('issue').get('user').get('login'),
                    e.repo.name,
                    e.created_at
                ), parse_mode='HTML')
            elif e.type == 'IssueCommentEvent':
                print('not supported')
                print(e.payload)
            else:
                print('not supported')
                print(e.type)
                print(e.payload)
                # bot.send_message(chat_id=chatid, text="{} for repo {} from {} at {} UTC"
                #                  .format(e.type, e.repo.name, e.actor.name, e.created_at))


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

    github_api_key = "bot:github:api:key"
    if REDIS_QUEUE.exists(github_api_key):
        prodrink = Github(REDIS_QUEUE.get(github_api_key).decode()).get_organization("prodrink")
    else:
        print('Prodrink Redis do not have GitHub API key')
        sys.exit(2)

    global updater

    telegram_api_key = "bot:telegram:api:key"

    if REDIS_QUEUE.exists(telegram_api_key):
        updater = Updater(REDIS_QUEUE.get(telegram_api_key).decode())
    else:
        print('Prodrink Redis do not have Telegram API key')
        sys.exit(2)

    updater.dispatcher.add_handler(CommandHandler('get', get))
    updater.dispatcher.add_handler(CommandHandler('scan', scan))
    updater.dispatcher.add_handler(CommandHandler('getall', getall))
    updater.dispatcher.add_handler(CommandHandler('set', set))
    updater.dispatcher.add_handler(CommandHandler('delete', delete))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    queue = updater.job_queue

    queue.run_repeating(callback_minute, interval=5 * 60.0, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(sys.argv[1:])
