from pymongo import MongoClient
import pymongo
import json
import pika
import time 
import RPi.GPIO as GPIO
import pickle


def main():
    # Set up Rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # Establish a channel
    channel = connection.channel()
    # Delete the local queue to clear it
    channel.queue_delete(queue='repository_queue')
    # Declare the local
    channel.queue_declare(queue='repository_queue')
    # Setup a consume for the local queue
    channel.basic_consume(on_request, queue='repository_queue')

    print(" [x] Waiting for Bridge Message")
    # Start consuming
    channel.start_consuming()


# Handles data available on the local repository queue
def on_request(ch, method, props, body):
    response = ''  # initialize response passed back to the bridge

    print('Message Recieved', body.decode('utf-8'))
    # Convert body to a json object
    message = json.loads(body.decode('utf-8'))

    if message['Action'] == 'push':
        # Create a message that doesn't have the action key/value pair to push to db
        message.pop('Action', None)
        response = handle_push_request(message)
    elif message['Action'] == 'pull':
        response = handle_pull_request(message)
    else:  # Should never reach this case
        response = [{"Status": "fail: Invalid action"}]

    ch.basic_publish(exchange='',
        routing_key=str(props.reply_to),
        properties=pika.BasicProperties(correlation_id = props.correlation_id),
        body=pickle.dumps(response))


# Stores the contents of the message into the local database; returns the count of posts
def store_json_message(msg):
    # Create a mono client
    client = MongoClient()

    # Load the database
    db = client.local_database

    # Get the posts of this database
    posts = db.posts

    # Try to push the json message into database
    try:
        print("Attempting to store ", msg, " into Repository database.")
        id = posts.insert_one(msg).inserted_id
        print("Successfully inserted message into Repository database ", id)
    except pymongo.errors.ServerSelectionTimeoutError:
        return -1  # Error
    return db.posts.count()


# This function handles a pull request from the mobile pi, returns a list of responses
def handle_pull_request(message):
    # Get responses for subjects if needed
    if 'Message' in message:  # Has criteria for message and subject
        # get list of posts that fit criteria indicated
        posts = get_documents('Subject', message['Subject'], 'Message', message['Message'])

        # return the messages that fit criteria or return no messages found
        if len(posts) is 0:
            return [{'Status': 'fail: no messages found with criteria'}]
        else:
            # append the status to the end of the list
            posts.append({'Status': 'success'})
            return posts
    else: # only specifies message criteria
        # get list of posts that fit criteria indicated
        posts = get_documents('Subject', message['Subject'], 'Message', '.*')

        # return the messages that fit criteria or return no messages found
        if len(posts) is 0:
            return [{'Status': 'fail: no messages found with criteria'}]
        else:
            # append the status to the end of the list
            posts.append({'Status': 'success'})
            return posts
    # return the responses


def handle_push_request(message):
    count = store_json_message(message)  # try to post message in db
    if count is -1:
        return [{'Status': 'fail: message not added to database'}]  # send fail response
    else:
        msgCounter(count)  # display the new message count on led
        return [{'Status': 'success: message added to database'}]  # send success response


def get_documents(key, value, key2, value2): 
    print('Searching Key \'', key, '\' with regex value \'', value, '\' and Key \'', key2, '\' with regex value \'', value2, '\'')

    # Create a mongo client
    client = MongoClient()

    # Load the database
    db = client.local_database

    # Get the posts of this database
    posts = db.posts

    # Find messages that meet regular expression passed in
    messages = list(posts.find({"$and": [{key: {'$regex': value}}, {key2:{'$regex': value2}}]}))
    for m in messages:
        del m['_id']
    print(messages)
    return messages


# This function implements a method to display the count onto the LED
def msgCounter(tot):
    # Disable the warnings
    GPIO.setwarnings(False)
    # Setup the GPIO Mode
    GPIO.setmode(GPIO.BCM)
    # Set the pins to outputs
    GPIO.setup(4, GPIO.OUT)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)

    # Compute the number corresponding to each decimal place
    sleep_time = 1        # one second sleep time
    ones = int(tot%10)            # get the number of ones
    tens = int((tot%100-ones)/10)    # get the number of tens
    hunds = int((tot-tot%100)/100)    # get the number of hundreds

    # send the LED values so that it is turned off
    GPIO.output(4, GPIO.LOW)
    GPIO.output(17, GPIO.LOW)
    GPIO.output(27, GPIO.LOW)

    # for the number of hundreds
    for digit in range(0, hunds):
        GPIO.output(4, GPIO.HIGH)    # turn red on
        time.sleep(sleep_time)        # delay for sleep time
        GPIO.output(4, GPIO.LOW)    # turn red off
        time.sleep(sleep_time)        # delay for sleep time

    # for the number of tens
    for digit in range(0, tens):
        GPIO.output(17, GPIO.HIGH)    # turn green on
        time.sleep(sleep_time)        # delay for sleep time
        GPIO.output(17, GPIO.LOW)    # turn green off
        time.sleep(sleep_time)        # delay for sleep time

    # for the number of ones
    for digit in range(0, ones):
        GPIO.output(27, GPIO.HIGH)    # turn blue on
        time.sleep(sleep_time)        # delay for sleep time
        GPIO.output(27, GPIO.LOW)    # turn blue off
        time.sleep(sleep_time)        # delay for sleep time


if __name__ == "__main__":
    main()
