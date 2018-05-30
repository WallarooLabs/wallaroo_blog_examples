import socket
import sys
import requests
import requests_oauthlib
import json
import struct

# Replace the values below with yours
ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_SECRET)


def send_tweets_to_wallaroo(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            if 'text' in full_tweet:
                tweet_text = full_tweet['text'].encode('utf-8')
                tweet_text_length =  len(tweet_text)
                if tweet_text_length > 0:
                    send_data = struct.pack(">I%ds" % tweet_text_length, tweet_text_length, tweet_text)
                    tcp_connection.sendall(send_data)
        except:
            print "Error decoding data received from Twitter!"


def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('locations', '-130,-20,100,50'), ('track', '#')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    return response


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to Wallaroo
wallaro_input_address = ('localhost', 8002)

print 'connecting to Wallaroo on %s:%s' % wallaro_input_address
sock.connect(wallaro_input_address)

resp = get_tweets()
send_tweets_to_wallaroo(resp,sock)



