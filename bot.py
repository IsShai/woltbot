#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
print(datetime.datetime.now())


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ids = [12211916]
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def ok(bot, update):
    # bot.send_photo(chat_id=update.chat_id, photo=open('C:\Users\quick\Desktop\Untitled.png', 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open('C:\\Users\\quick\\Desktop\\download.png', 'rb'))

def subscribe(bot, update, job_queue):
    """Echo the user message."""
    bot.send_message(chat_id=update.message.chat_id, text='Starting!')
    # job_queue.run_repeating(callback_alarm, 1, context=update.message.chat_id)
    t = datetime.time(hour= 0, minute=21)
    job_queue.run_daily(callback_alarm, datetime.time(hour=0, minute=46), days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)
    job_queue.run_daily(callback_alarm, datetime.time(hour=0, minute=48), days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)
    job_queue.run_daily(callback_alarm, datetime.time(hour=0, minute=47), days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)
    job_queue.run_daily(callback_alarm, datetime.time(hour=0, minute=49), days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)


def callback_alarm(update, job):
    update.send_message(chat_id=job.context, text='Wolt!!')

def stop_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Stoped!')
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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("sub", subscribe, pass_job_queue=True))
    dp.add_handler(CommandHandler("ok", ok))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()