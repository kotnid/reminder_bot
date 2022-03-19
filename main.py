from logging import info , basicConfig , INFO
from pymongo import MongoClient
from os import environ
from telebot import TeleBot
from threading import Thread

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# logging config 
basicConfig(level= INFO,
            format= '%(asctime)s %(levelname)s %(message)s',
            datefmt= '%Y-%m-%d %H:%M')

# mongodb client setup
client = MongoClient('mongodb+srv://tkt_bot_version1:{}@cluster0.tu30q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'.format(environ['pw']))
db = client['reminder_bot']
job_db = db['jobs']

# telebot setup
botToken = environ['token']
bot = TeleBot(botToken,  parse_mode=None)



# start both job 
if __name__ == "__main__":
    Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    
    scheduler = AsyncIOScheduler()
    Thread(target=scheduler.start , name='scheduler.start' , daemon=True).start()

    asyncio.get_event_loop().run_forever()