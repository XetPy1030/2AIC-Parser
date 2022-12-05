import json

with open('db.json', 'rb') as f:
    users = json.load(f)

def save():
    file = open('db.json', 'w')
    file.write(json.dumps(users))
    file.close()

def get_last_object(user_id):
    user_id = str(user_id)
    return users[user_id]

def set_last_object(user_id, object):
    user_id = str(user_id)
    users[user_id] = object

def is_user_in_db(user_id):
    return str(user_id) in users.keys()