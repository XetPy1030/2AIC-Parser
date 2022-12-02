import json

users = json.load(open('db.json', 'rb'))

def save():
    file = open('db.json', 'w')
    file.write(json.dumps(users))
    file.close()

def get_last_object(id):
    return users[id]

def set_last_object(id, object):
    users[id] = object

def is_user_in_db(id):
    return id in users.keys()