# Wallaroo Twitter Trending Hashtags

## Description

The Twitter Trending Hashtags application receives a stream of tweets via the Twitter Streaming API and keeps a running count to identify the top trending hashtags. This information is then forwarded to a web UI and displayed to the user.

You can learn more about this example from [our blog post](https://blog.wallaroolabs.com/2018/06/stream-processing-trending-hashtags-and-wallaroo/).

## Requirements

- [Wallaroo 0.4.x](https://github.com/WallarooLabs/wallaroo/tree/0.4.1)
- Python 2.7.x
- Python Modules:
  - flask
  - requests_oauthlib

## Installation

- Install Python dependencies

```bash
pip install -r requirements.txt
```

- Install Wallaroo Python API

See the [Wallaroo documention](https://docs.wallaroolabs.com/book/getting-started/choosing-an-installation-option.html) for installation instructions.

## Configuration

You'll need to setup an account with Twitter to access their firehose and copy some access tokens into the `twitter_client.py` script. In order to get real-time tweets, you need to register on [Twitter Apps](https://apps.twitter.com/) by clicking on “Create new app”, and filling in the form under “Create your twitter app”. 

Once you have done that, go to your newly created app and open the “Keys and Access Tokens” tab, then click on “Create my access token”.

You'll need to update `twitter_client.py` will the values for you application:

```python
# Replace the values below with yours
ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
```

## Running Instructions

4 terminals are required to run the various components of this application.

1 each for:

- Twitter client
- Wallaroo
- Wallaroo to Web UI bridge
- Web UI

From within the directory for this application you will need to:

- Start the Web UI

```bash
python app.py
```

- Start the Wallaroo to Web UI bridge

```bash
python socket_receiver.py
```

- Start Wallaroo

```bash
bash worker1
```

- Start the Twitter client

```bash
python twitter_client.py
``` 

- Check out the results as they come in:

[http://localhost:5003/](http://localhost:5003/)

