from logging import info , basicConfig , INFO
from pymongo import MongoClient
from os import environ

# logging config 
basicConfig(level= INFO,
            format= '%(asctime)s %(levelname)s %(message)s',
            datefmt= '%Y-%m-%d %H:%M')

# mongodb client setup
client = MongoClient('mongodb+srv://tkt_bot_version1:{}@cluster0.tu30q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'.format(environ['pw']))
db = client['reminder_bot']
job_db = db['jobs']
