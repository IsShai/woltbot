#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
import random
import math

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getRandomInt():
    return str(math.floor(random.random() * (10000 - 5)) + 4)

def pic(bot, update):
    # bot.send_photo(chat_id=update.chat_id, photo=open('C:\Users\quick\Desktop\Untitled.png', 'rb'))
    imgUrl = "http://graph.facebook.com/v2.5/" + getRandomInt() + "/picture?height=200&height=200"
    bot.send_photo(chat_id=update.message.chat_id, photo=imgUrl)
    logger.info('User {} just got this pic {}'.format(update.effective_user.full_name, imgUrl))

def subscribe(bot, update, job_queue):

    bot.send_message(chat_id=update.message.chat_id, text='Hey {}, subscribe done'.format(update.effective_user.full_name))
    # to get utc time - minus 3 to the hour
    # 11 is 8 and so on
    job_queue.run_daily(callback_alarm1, datetime.time(hour=8, minute=30), days=(0, 1, 2, 3, 4, 5, 6), context=(update.message.chat_id, update.effective_user.full_name))
    job_queue.run_daily(callback_alarm2, datetime.time(hour=13, minute=0), days=(0, 1, 2, 3, 4, 5, 6), context=(update.message.chat_id, update.effective_user.full_name))
    logger.info('User {} just subscribed'.format(update.effective_user.full_name))

def callback_alarm1(update, job):
    update.send_message(chat_id=job.context[0], text='Wolt!')
    update.send_message(chat_id=job.context[0], text='Will remaind you again in a few hours')
    logger.info('User {} just got alarm1 msg'.format(job.context[1]))



def callback_alarm2(update, job):
    update.send_message(chat_id=job.context[0], text='Wolt!!!')
    logger.info('User {} just got alarm2 msg'.format(job.context[1]))


def unsubscribe(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Bey {} ,unsubscribe done!'.format(update.effective_user.full_name))
    logger.info('User {} just unsubscribed'.format(update.effective_user.full_name))
    job_queue.stop()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1279373046:AAGk1eH7lD8MZqNFT8VDyuAoO2Zrlkv1I4Q", use_context=False)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    dp.add_handler(CommandHandler("sub", subscribe, pass_job_queue=True))
    dp.add_handler(CommandHandler("unsub", unsubscribe, pass_job_queue=True))
    dp.add_handler(CommandHandler("pic", pic))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()