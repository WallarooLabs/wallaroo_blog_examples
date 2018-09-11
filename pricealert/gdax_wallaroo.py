from __future__ import print_function

import json
import os
import signal
import socket
import sys
import time
import struct

import cbpro
import requests
import requests_oauthlib


def send_to_wallaroo(message, tcp_connection):
    try:
        tcp_connection.sendall(struct.pack(">I",len(message))+message)
    except:
        print("Error decoding data received from Coinbase!")


class coinbaseWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["BTC-USD"]
        self.message_count = 0
        print("Lets count the messages!")

    def on_message(self, msg):
        if 'price' in msg and 'type' in msg:
            self.message_count += 1
            send_to_wallaroo(json.dumps(msg), sock)
            print("Message type:", msg["type"],
                  "\t@ {:.3f}".format(float(msg["price"])))

    def on_close(self):
        print("-- Goodbye! --")


print("Set up Coinbase websocket....")
wsClient = coinbaseWebsocketClient()
wsClient.start()

print("Set up Wallaroo socket.....")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wallaro_input_address = ('localhost', 7000)

print("connecting to Wallaroo on {}".format(wallaro_input_address))
sock.connect(wallaro_input_address)

print(wsClient.url, wsClient.products)
while (wsClient.message_count < 10000):
    print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
    time.sleep(0.5)
wsClient.close()
