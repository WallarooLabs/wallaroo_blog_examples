# Wallaroo Twitter Trending Hashtags

## Description

The Twitter Trending Hashtags application receives a stream of tweets via the Twitter Streaming API and keeps a running count to identify the top trending hashtags. This information is then forwarded to a web UI and displayed to the user.

## Requirements

- [Wallaroo 0.2.2](https://github.com/WallarooLabs/wallaroo/tree/0.2.2)
	**NOTE:** This is incompatible with Wallaroo 0.4.0 and up due to an API change, see [How to Update your Wallaroo Python Applications to the new API](https://blog.wallaroolabs.com/2018/01/how-to-update-your-wallaroo-python-applications-to-the-new-api/) to bring this example up to date if needed.
- Python 2.7.x
- Python Modules:
  - flask
  - requests_oauthlib
  - pandas

## Running Instructions

Instructions on setting up and running this example can be found in the [Identifying Trending Twitter Hashtags in Real-time with Wallaroo](https://blog.wallaroolabs.com/2017/11/identifying-trending-twitter-hashtags-in-real-time-with-wallaroo/) blog post.
