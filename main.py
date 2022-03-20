from calendar import week
from logging import info , basicConfig , INFO
from pymongo import MongoClient
from os import environ
from telebot import TeleBot
from threading import Thread
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from uuid import uuid4

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


class Reminder:
    def __init__ (self , id):
        self.id = id
        self.msg = None

user_dict = {}

# add reminder
@bot.message_handler(commands=['add_re'])
def add(message):
    check_ac(message.from_user)

    bot.send_message(message.from_user.id , 'What is the message of the reminder ? (E.g. Watch k-on now)')
    bot.register_next_step_handler_by_chat_id(message.from_user.id , process_msg_step)
    '''
    text = message.text.split()[1:]
    scheduler.add_job(send_message, 'interval', id='temp' , seconds=30 , kwargs={"id" : message.from_user.id , "message":str(text)})

    myquery = {'_id' : message.from_user.id}
    data = job_db.find_one(myquery)

    data['jobs'].append({'id' : 'temp' , 'type' : 'interval' , 'seconds' : 30 , 'message' : str(text)}) 
    job_db.update_one({'_id' : message.from_user.id} , {'$set' : {'jobs' : data['jobs']}})
    '''

def process_msg_step(message):
    reminder = Reminder(message.from_user.id)
    reminder.msg = message.text
    user_dict[message.from_user.id] = reminder

    bot.send_message(message.from_user.id , 'date or interval or cron ?')
    bot.register_next_step_handler_by_chat_id(message.from_user.id , process_type_step)
    
    

def process_type_step(message):
    if message.text == 'interval':
        bot.send_message(message.from_user.id , 'Interval how much? (E.g. h 2 -> each 2 hour run)')
        bot.register_next_step_handler_by_chat_id(message.from_user.id , process_interval_step)

    elif message.text == 'cron':
        pass

    elif message.text == 'date':
        bot.send_message(message.from_user.id , 'When to send? (E.g. d/m/y H:M -> 03/12/11 01:50)')
        bot.register_next_step_handler_by_chat_id(message.from_user.id , process_date_step)

    else:
        bot.reply_to(message , 'Invalid input , pls try again')
        bot.register_next_step_handler_by_chat_id(message.from_user.id , process_type_step)

def process_date_step(message):
    try:
        id = message.from_user.id
        myquery = {'_id' : id}
        data = job_db.find_one(myquery)

        if len(data['jobs']) > 10:
            bot.send_message(id , 'Maximum reminder reached')
            return ''

        job_id = str(id)+ '_' +str(uuid4()).replace('-','').upper()[0:4]

        reminder = user_dict[id]

        datetime_obj = datetime.strptime(message.text, '%d/%m/%y %H:%M')

        scheduler.add_job(send_message , 'date' ,id=job_id ,  run_date = datetime_obj , kwargs={'id':id  , 'message': reminder.msg})

        data['jobs'].append({'id' : job_id, 'type' : 'date'  , 'datetime' : datetime_obj , 'message' : reminder.msg}) 
        job_db.update_one({'_id' : id} , {'$set' : {'jobs' : data['jobs']}})

        info('User {} added job'.format(id))


    except Exception as e:
        print(e)
        bot.reply_to(message , 'Invalid input , pls try again')
        bot.register_next_step_handler_by_chat_id(message.from_user.id , process_date_step)

def process_interval_step(message):
    time_type = message.text.split()[0]
    interval = message.text.split()[1]
    
    if time_type == 'w':
        scheduler_add_interval_job('w' , interval , message.from_user.id)
    elif time_type == 'd':
        scheduler_add_interval_job('d' , interval , message.from_user.id)
    elif time_type == 'h':
        scheduler_add_interval_job('h' , interval , message.from_user.id)
    else:
        bot.reply_to(message , 'Invalid input , pls try again')
        bot.register_next_step_handler_by_chat_id(message.from_user.id , process_interval_step)


def scheduler_add_interval_job(time_type , interval , id):
    myquery = {'_id' : id}
    data = job_db.find_one(myquery)

    if len(data['jobs']) > 10:
        bot.send_message(id , 'Maximum reminder reached')
        return ''

    reminder = user_dict[id]

    job_id = str(id)+ '_' +str(uuid4()).replace('-','').upper()[0:4]

    try:
        if time_type == 'w':
            scheduler.add_job(send_message , 'interval' ,id=job_id ,  weeks=int(interval) , kwargs={'id':id  , 'message': reminder.msg})

            data['jobs'].append({'id' : job_id, 'type' : 'interval'  , 'arg' : 'weeks' , 'amount' : interval, 'message' : reminder.msg}) 
            job_db.update_one({'_id' : id} , {'$set' : {'jobs' : data['jobs']}})

            info('User {} added job'.format(id))

        elif time_type == 'd':
            scheduler.add_job(send_message , 'interval' ,id=job_id ,  days=int(interval) , kwargs={'id':id  , 'message': reminder.msg})

            data['jobs'].append({'id' : job_id, 'type' : 'interval'  , 'arg' : 'days' , 'amount' : interval, 'message' : reminder.msg}) 
            job_db.update_one({'_id' : id} , {'$set' : {'jobs' : data['jobs']}})

            info('User {} added job'.format(id))

        elif time_type == 'h':
            scheduler.add_job(send_message , 'interval' ,id=job_id ,  hours=int(interval) , kwargs={'id':id  , 'message': reminder.msg})

            data['jobs'].append({'id' : job_id, 'type' : 'interval'  , 'arg' : 'hours' , 'amount' : interval, 'message' : reminder.msg}) 
            job_db.update_one({'_id' : id} , {'$set' : {'jobs' : data['jobs']}})

            info('User {} added job'.format(id))

    except Exception as e:
        print(e)
        bot.send_message(id , 'Www u so lucky , it is rare to happen this error')
        #scheduler_add_interval_job(time_type , interval , id)


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

# remove reminder
@bot.message_handler(commands=['remove_re'])
def remove(message):
    check_ac(message.from_user)
    text = message.text.split()[1]
    
    print(text)

    myquery = {'_id' : message.from_user.id}
    data = job_db.find_one(myquery)

    for job in data['jobs']:
        if text == job['id']:
            data['jobs'].remove(job)
            break
    
    job_db.update_one({'_id' : message.from_user.id} , {'$set' : {'jobs' : data['jobs']}})

# start both job 
if __name__ == "__main__":
    Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    
    scheduler = AsyncIOScheduler()
    Thread(target=scheduler.start , name='scheduler.start' , daemon=True).start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass