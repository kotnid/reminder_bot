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

def send_message(id , message):
    bot.send_message(id , message)

# check if account is created 
def check_ac(message):
    id = message.id
    myquery = {'_id' : id}
    if job_db.count_documents(myquery) == 0 :
            data = {'_id' : id , 'name' : message.first_name , 'jobs':[] }
            info("User {} with id {} created account".format(message.first_name , str(id)))
            job_db.insert_one(data)

# add reminder
@bot.message_handler(commands=['add_re'])
def add(message):
    check_ac(message.from_user)
    text = message.text.split()[1:]
    scheduler.add_job(send_message, 'interval', id='temp' , seconds=30 , kwargs={"id" : message.from_user.id , "message":str(text)})

    myquery = {'_id' : message.from_user.id}
    data = job_db.find_one(myquery)

    data['jobs'].append({'id' : 'temp' , 'type' : 'interval' , 'seconds' : 30 , 'message' : str(text)}) 
    job_db.update_one({'_id' : message.from_user.id} , {'$set' : {'jobs' : data['jobs']}})

# check reminder
@bot.message_handler(commands=['check_re'])
def check(message):
    check_ac(message.from_user)

    myquery = {'_id' : message.from_user.id}
    data = job_db.find_one(myquery)

    msg = 'Here is job scheduled : '+'\n'
    for job in data['jobs']:
        msg += '{} : {}'.format(job['id'] , job['message']) + '\n'

    bot.reply_to(message , msg)


# start both job 
if __name__ == "__main__":
    Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    
    scheduler = AsyncIOScheduler()
    Thread(target=scheduler.start , name='scheduler.start' , daemon=True).start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass