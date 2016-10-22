import sys
import json
import time
from pymongo import MongoClient
import pymongo
from bluetooth import *


def main():
    # Parse command line arguments
    action, subject, text = parse_arguments(sys.argv)
    print("Action = " + action + " Subject = " + subject + " Text = " + text)

    # If the action is a pull
    if action == 'pull':
        # Construct a pull request object
        raw, msg = construct_pull_object(subject, text)
        print("Pull Request: ", msg)
        # Store the raw dictionary object into the local database
        store_json_message(raw)
        # Send the request to the bridge over bluetooth
        sendBluetooth(msg)
        # Wait and receive a response from the bridge over bluetooth
        recvBlueooth()
    # if the action is a push
    elif action == 'push':
        # Construct a push request object
        raw, msg = construct_push_object(subject, text)
        print("Push Request: ", msg)
        # Store the raw dictionary object into the local database
        store_json_message(raw)
        # Send the request to the bridge over bluetooth
        sendBluetooth(msg)
        # Wait and receive a response from the bridge over bluetooth
        recvBlueooth()
    # Error
    else:
        sys.exit('Error: Invalid action!')

# Sends a message to the bridge
def sendBluetooth(msg):
    # Establish a connection
    sock = BluetoothSocket(RFCOMM)
    port = 1
    sock.connect(('B8:27:EB:F5:49:CC', port))
    # Send the message to the receiver
    sock.send(msg)
    sock.close()

# Receives a message from the bridge
#   Prints out the responses and waits for a status json object to be sent over
def recvBlueooth():
    # Establish a connection
    server_sock = BluetoothSocket(RFCOMM)
    port = 1
    server_sock.bind(("", port))

    # Wait for a connection
    server_sock.listen(1)
    client_sock, address = server_sock.accept()
    print("Accepted connection from ", address)

    # Receive from bluetooth
    print('Response from repository\n')
    while True:
        # Receive from the bridge
        data = client_sock.recv(1024)
        print(json.loads(data.decode('utf-8')))
        # If the current data has a status key then break out of the while loop
        if 'Status' in json.loads(data.decode('utf-8')):
            break
    # Close the connection
    client_sock.close()
    server_sock.close()


# Store the json object into the local database
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
        posts.insert_one(msg)
        print("Successfully inserted message into local database")
    except pymongo.errors.ServerSelectionTimeoutError:
        # Error
        sys.exit("Error: No instance of Mongod running")


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


# Constructs a push object; Returns the raw dictionary and the string formatted version
def construct_push_object(subject, message):
    # Create a dictionary
    data = dict()
    # Set the action
    data['Action'] = "push"
    # Set the message id
    data['MsgID'] = "10" + "$" + str(time.time())
    # If the subject is present then set the subject
    if subject != "":
        data['Subject'] = subject
    # If the message is present then set the message
    if message != "":
        data['Message'] = message
    return data, json.dumps(data, sort_keys=True)

# Constructs a pull object; Returns the raw dictionary and the string formatted version
def construct_pull_object(subject, message):
    # Create a dictionary
    data = dict()
    # Set the action
    data['Action'] = "pull"
    # If the subject is present then set the subject
    if subject != "":
        data['Subject'] = subject
    # If the message is present then set the message
    if message != "":
        data['Message'] = message
    return data, json.dumps(data, sort_keys=True)


if __name__ == "__main__":
    main()
