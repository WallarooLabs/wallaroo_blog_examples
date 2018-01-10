import socket
import sys
import requests
import requests_oauthlib
import json

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
                # send the length of text + 1 for newline represented as 5 ASCII
                # characters, followed by the tweet text and \n
                # e.g. if tweet text is 'Hello everyone!', send '00016Hello everyone!'
                tcp_connection.sendall(str(len(tweet_text)+1).zfill(5) +
                        tweet_text + '\n')
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



