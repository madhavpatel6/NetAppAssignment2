import sys
import json
import time
from pymongo import MongoClient
import pymongo


def main():
    # Parse command line arguments
    action, subject, text = parse_arguments(sys.argv)
    print("Action = " + action + " Subject = " + subject + " Text = " + text)
    if action == 'pull':
        raw, msg = construct_pull_object(subject, text)
        print("Pull Request: ", msg)
        store_json_message(raw)
    elif action == 'push':
        raw, msg = construct_push_object(subject, text)
        store_json_message(raw)
        print("Push Request: ", msg)
    else:
        sys.exit('Error: Invalid action!')
    print(get_documents('Action', 'push'))


def store_json_message(msg):
    # Create a mongo client
    client = MongoClient()
    # Load the database
    db = client.local_database
    # Get the posts of this database
    posts = db.posts
    # Try to push the json message into database
    try:
        print("Attempting to store ", msg, " into local database.")
        id = posts.insert_one(msg).inserted_id
        print("Successfully inserted message ", id)
    except pymongo.errors.ServerSelectionTimeoutError:
        # Error
        sys.exit("Error: No instance of Mongod running")


def get_documents(key, value):
    print('Searching Key \'', key, '\' with regex value \'', value, '\'')
    # Create a mongo client
    client = MongoClient()
    # Load the database
    db = client.local_database
    # Get the posts of this database
    posts = db.posts
    # Try to push the json message into database
    return list(posts.find({key: {'$regex': value}}))


# This function will parse in the command line arguments
def parse_arguments(args):
    itr = 0
    action = ""
    subject = ""
    text = ""
    # Iterate through the while loop
    while itr < len(args):
        # If the current argument is -a then store the action
        if args[itr] == "-a" and itr + 1 < len(args):
            action = args[itr + 1]
        # else if the current argument is -s then store the subject
        elif args[itr] == "-s" and itr + 1 < len(args):
            subject = args[itr + 1]
        # else if the current argument is -m then store the text
        elif args[itr] == "-m" and itr + 1 < len(args):
            text = args[itr + 1]
        itr += 1
    return action, subject, text


def construct_push_object(subject, message):
    data = dict()
    data['Action'] = "push"
    data['MsgID'] = "team_10" + "$" + str(time.time())
    if subject != "":
        data['Subject'] = subject
    if message != "":
        data['Message'] = message
    return data, json.dumps(data, sort_keys=True)#, indent=4)


def construct_pull_object(subject, message):
    data = dict()
    data['Action'] = "pull"
    if subject != "":
        data['Subject'] = subject
    if message != "":
        data['Message'] = message
    return data, json.dumps(data, sort_keys=True)#, indent=4)


if __name__ == "__main__":
    main()
