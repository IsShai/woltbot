#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

PORT = int(os.environ.get('PORT', 5000))
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from time import sleep
import datetime
import pymongo
import random

class DailyBot:

    def __init__(self, token):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

        # connecting to mongo
        client = pymongo.MongoClient(
            "MONGO_STRING")
        db = client.wolt
        userCol = db["users"]
        factsCol = db["facts"]

        self.NUM_OF_FACTS = 592
        self.userCollection = userCol
        self.factCollection = factsCol
        self.logger = logging.getLogger("LOG")
        self.logger.info("Starting BOT.")
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        self.job = self.updater.job_queue

        dayTimeMsg1 = datetime.time(hour=9,  minute=0)
        dayTimeMsg2 = datetime.time(hour=12, minute=0)
        dayTimeMsg3 = datetime.time(hour=14, minute=0)

        self.job_daily = self.job.run_daily(self.send_daily_first, time=dayTimeMsg1, days=(0, 1, 2, 3, 6), )
        self.job_daily = self.job.run_daily(self.send_daily_first, time=dayTimeMsg2, days=(0, 1, 2, 3, 6), )
        self.job_daily = self.job.run_daily(self.send_daily_first, time=dayTimeMsg3, days=(0, 1, 2, 3, 6), )

        ## at night need to update all redeem values to false
        dayTimeForRedeemRestore = datetime.time(hour=21, minute=55)
        self.job_daily = self.job.run_daily(self.update_daily_redeem, time=dayTimeForRedeemRestore,
                                            days=(0, 1, 2, 3, 6), )

        subscribe_handler = CommandHandler("sub", self.subscribe)
        self.dispatcher.add_handler(subscribe_handler)

        unsubscribe_handler = CommandHandler("unsub", self.unsubscribe)
        self.dispatcher.add_handler(unsubscribe_handler)

        redeem_handler = CommandHandler("redeem", self.redeem)
        self.dispatcher.add_handler(redeem_handler)

        fact_handler = CommandHandler("fact", self.fact)
        self.dispatcher.add_handler(fact_handler)

        self.dispatcher.add_error_handler(self.error)

    @staticmethod
    def send_type_action(chatbot, update):
        """
        Shows status typing when sending message
        """
        chatbot.send_chat_action(
            chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING
        )
        sleep(1)

    def send_daily_first(self, bot, update):
        self.logger.info("print from send daily.")
        users = self.userCollection.find({})

        for user in users:
            isRedeem = user['redeem']
            if isRedeem == False:
                userId = user['userId']
                bot.send_message(chat_id=userId, text='Wolt!')

    def subscribe(self, bot, update):
        # self.update_daily_redeem()
        user = {"name": update.effective_user.full_name, "userId": update.effective_user.id, "redeem": False,
                "nickname": update.effective_user.name}
        isExsit = self.userCollection.find_one({"userId": update.effective_user.id})

        if isExsit is None:
            self.userCollection.insert_one(user)
            self.logger.info('user {} just subscribe'.format(update.effective_user.full_name))
            bot.send_message(chat_id=update.message.chat_id,
                             text='Hey {}, subscribe done'.format(update.effective_user.full_name))

        else:
            self.logger.info('user {} just subscribe'.format(update.effective_user.full_name))
            bot.send_message(chat_id=update.message.chat_id,
                             text='Hey {}, you are already subscribed'.format(update.effective_user.full_name))

    def unsubscribe(self, bot, update):
        user = {"userId": update.effective_user.id}
        isExsit = self.userCollection.find_one(user)
        if isExsit is None:
            bot.send_message(chat_id=update.message.chat_id,
                             text='{} ,you are already unsubscribed'.format(update.effective_user.full_name))
        else:
            self.userCollection.delete_one(user)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Bey {} ,unsubscribe done!'.format(update.effective_user.full_name))
            self.logger.info('User {} just unsubscribed'.format(update.effective_user.full_name))

    def redeem(self, bot, update):

        user = self.userCollection.find_one({"userId": update.effective_user.id})

        if user is not None:
            # need to update that the user is got his wolt
            user['redeem'] = True
            self.userCollection.replace_one({'_id': user['_id']}, user)
            self.logger.info('user {} just got his wolt'.format(update.effective_user.full_name))
            bot.send_message(chat_id=update.message.chat_id,
                             text='Hey {}, Thanks for the Update'.format(update.effective_user.full_name))

        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Hey {}, you need to subscribe first by /sub'.format(update.effective_user.full_name))

    def fact(self, bot, update):
        # self.update_daily_redeem()

        isExsit = self.userCollection.find_one({"userId": update.effective_user.id})

        if isExsit is None:
            self.logger.info('user {} just asked for fact, but not subscribed'.format(update.effective_user.full_name))
            bot.send_message(chat_id=update.message.chat_id,
                             text='Hey {}, you need to subscribe for this feature by /sub'.format(update.effective_user.full_name))


        else:
            num = random.randint(0, self.NUM_OF_FACTS)
            factObj = self.factCollection.find_one({"num": num})
            if factObj is not None:
                factString = factObj['fact']
                bot.send_message(chat_id=update.message.chat_id, text=factString)
                self.logger.info('User {} just got this fact {}'.format(update.effective_user.full_name, factString))
            else:
                bot.send_message(chat_id=update.message.chat_id, text="Something went wrong, please try again")
                self.logger.info('User {} just FAIL TO GET FACT {}'.format(update.effective_user.full_name, num))




    def update_daily_redeem(self, bot, update):

        users = self.userCollection.find({})
        # run all over the users
        for user in users:
            user['redeem'] = False
            self.userCollection.replace_one({'_id': user['_id']}, user)

        self.logger.info("all users redeem reser")
        return 0

    def error(self, chatbot, update, error):
        self.logger.warning(f'Update "{update}" caused error "{error}"')
        return 0

    def run(self, token):
        # Start the Bot
        self.logger.info("Polling BOT.")
        # heroku polling

        self.updater.start_webhook(listen="0.0.0.0",
                                   port=int(PORT),
                                   url_path=token)
        self.updater.bot.setWebhook('YOUR_HEROKU_APP_URL/' + token)
        # self.updater.start_polling()

        # Run the BOT until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the BOT gracefully.
        self.updater.idle()
        return 0


if __name__ == '__main__':
    TOKEN = "BOT_TOKEN"

    # Run on local system once detected that it's not on Heroku nor ngrok
    BOT = DailyBot(TOKEN)
    BOT.run(TOKEN)
