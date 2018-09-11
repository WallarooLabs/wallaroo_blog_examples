from __future__ import print_function
import os
import time
import django

# This is needed because we are running this outside of django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricealert.settings")
django.setup()

import cbpro
from djmoney.money import Money

from pricealertweb.models import MarketData

class coinbaseWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["BTC-USD"]
        self.message_count = 0
        print("Lets count the messages!")

    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg:
            MarketData.objects.create(
                price=Money(msg["price"], 'USD')
            )
            print("Message type:", msg["type"],
                  "\t@ {:.3f}".format(float(msg["price"])))

    def on_close(self):
        print("-- Goodbye! --")


wsClient = coinbaseWebsocketClient()
wsClient.start()
print(wsClient.url, wsClient.products)
while (wsClient.message_count < 1000):
    print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
    time.sleep(0.5)
wsClient.close()
