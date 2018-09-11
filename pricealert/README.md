# pricealert

This is a companion application designed to show the difference between batch processing and stream processing. If you aren't familiar with either Batch or Stream processing there are good articles online. Many of the use-cases where you'd normally use batch processing are perfect use-cases for streaming.

In this application we use [Celery](http://docs.celeryproject.org/en/latest/index.html) to run our periodic tasks. We're going to use Wallaroo 0.5.2 do demonstrate taking our celery logic and converting it to Wallaroo.

There are quite a lot of opportunities to improve this application. Which we may explore in a future blog post.

## Installation and getting it running

If you don't have python 2.7.x, Redis or Wallaroo on your machine. Please find the correct installation instructions for Python and Redis for your operating system. You can find installation instructions for Wallaroo [here](https://docs.wallaroolabs.com/book/getting-started/choosing-an-installation-option.html) and all the different installations should work (docker, wallaroo-up, etc..)

Once those three dependencies are installed and this repo cloned, you'll need to install the needed python dependencies. Locally or with an already created [virtualenv environment](https://virtualenv.pypa.io/en/latest/installation/), inside the newly cloned repo run `pip install -r requirements.txt`.

The best way to get Wallaroo setup is to follow our "Run a Wallaroo Application in..." for whichever way you decided to install Wallaroo.

The easiest way to make sure everything works correctly, is to first set up Django.

```python
python manage.py migrate
```

Once Django is setup and you've done the necessary prerequisites for Wallaroo, you can run one of the following sets of commands.

#### For Celery in separate terminals:
```sh
# Seed our DB with some transactions from coinbase.
make gdax-celery
make django-celery-runserver
# It's important that you start celery last
make celery-run
```

#### For Wallaroo in separate terminals:

```sh
# Our custom receiver
make gdax-wallaroo-receiver
```
To run machida:

```sh
# Run our python code
machida --application-module coinbase  --in 127.0.0.1:7000,127.0.0.1:7001 \
  --out 127.0.0.1:5555 --metrics 127.0.0.1:5001 --control 127.0.0.1:6000 \
  --data 127.0.0.1:6001 --name worker-name --external 127.0.0.1:5050 \
  --cluster-initializer --ponythreads=1 --ponynoblock
```

Then start the webserver and application pulling data from coinbase
```sh
# Start webserver
make django-wallaroo-runserver
# Celery still needs to be started to trigger client side notifications and update our DB records
make celery-run
make gdax-wallaroo
```

## Contributing

Please create an issue/PR if you come across any issues.
