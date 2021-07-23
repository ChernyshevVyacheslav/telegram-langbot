import json
import os
from pymongo import MongoClient

client = MongoClient('mongodb', 27017)
db = client.langbot

class State:
    def __init__(self):
        if not os.path.exists('state.json'):
            with open('state.json', 'w+') as j:
                json.dump(dict("{}"), j)
            j.close()
        self.state = ''


    @property 
    def get(self):     
        return self.state

    
    def set_action(self, chat_id,  action):
        self.state[chat_id][0] = action

    def set_dest(self, chat_id, dest):
        self.state[chat_id][1] = dest


    def check(self, chat_id):
        chat_id = str(chat_id)
        if self.state == '':
            self.load(chat_id)
        if chat_id not in self.state:
            self.state[chat_id]=["reply", "en"]
        return chat_id


    def load(self, chat_id):
        with open('state.json', 'r') as j:
            jsonstate = json.load(j)
            if chat_id in jsonstate:
                self.state = {chat_id: [jsonstate[chat_id][0], jsonstate[chat_id][1]]}
            else:
                self.state = {chat_id: ["reply", "en"]}
            j.close()
    

        


    def save(self, chat_id):
        json_data = {}
        with open('state.json', 'r') as j:
            json_data = json.load(j)
        if isinstance(json_data, str):
            json_data = dict(eval(json_data))
        json_data[chat_id] = [self.state[chat_id][0], self.state[chat_id][1]]
        with open('state.json', 'w') as file:
            json.dump(json_data, file)
        j.close()
        file.close()

    
        







