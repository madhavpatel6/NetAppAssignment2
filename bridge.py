import pika
import json
from bluetooth import *


class BridgeClient(object):
    def __init__(self):
        crds = pika.PlainCredentials('guest', 'guest')
        # Create a connection to the repository
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rachaelpi.local', credentials=crds))
        # Create a channel with the connection
        self.channel = self.connection.channel()
        # Delete the bridge queue so we clear all the messages in the queue
        self.channel.queue_delete('bridge_queue')
        # Declare the bridge queue
        self.channel.queue_declare('bridge_queue')
        self.callback_queue = 'bridge_queue'
        # Setup a callback function for the bridge queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def __del__(self):
        self.connection.close()

    def on_response(self, ch, method, props, body):
        # Get the message
        self.response = body

    def call(self, n):
        self.response = None
        # Try to send the message to the repository via RabbitMQ
        try:
            self.channel.basic_publish(exchange='', routing_key='repository_queue', properties=pika.BasicProperties(reply_to = str('bridge_queue')), body=str(n))
            # Wait for a response
            while self.response is None:
                self.connection.process_data_events()
        except:
            return 'Error'
        # Return the response
        return self.response

    def sendBluetooth(msg):
        # Send message
        sock = BluetoothSocket(RFCOMM)
        port = 1
        sock.connect(('B8:27:EB:CC:AD:05', port))
        sock.send(msg)
        sock.close()

    def recvBlueooth():
        # Establish a connection
        server_sock = BluetoothSocket(RFCOMM)
        port = 1
        server_sock.bind("", port)

        # Wait for a connection
        server_sock.listen(1)
        client_sock, address = server_sock.accept()
        print("Accepted connection from ", address)

        # Receive from bluetooth
        data = client_sock.recv(1024)
        print('Response:\n', data)

        client_sock.close()
        server_sock.close()
        return data


def main():
    # Create a connection to the repository
    bridge = BridgeClient()
    while True:
        # Receive from bluetooth
        response = bridge.recvBlueooth()
        print('Request from the mobile\n', response)
        # Call into the bridge class
        recv_response = bridge.call(response)
        print('Received response from repository\n', recv_response)
        # Receive a response from the repository and then send it back over bluetooth
        bridge.sendBluetooth(recv_response)
        print('Sent response to mobile')

if __name__ == "__main__":
    main()
