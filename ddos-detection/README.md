# DDoS Detection Example in Wallaroo

## Description

The DDoS Detection application receives a stream of requests including a timestamp, client IP, server IP, and requested resource. It then partitions the data by server, maintains a counter of unique clients per second and total requests per second for the last 60 seconds. These data are then used to compute several statistical properties and determine whether a particular server is experiencing a sudden and abnormally high load (e.g. a DoS or DDoS attack).

Once a server is identified as under a DoS or DDoS attack, it reports to the aggregate health view, which emits a health status list for all of the servers each second, reporting their average load, current load, and whether they are suspected to be under a DoS or DDoS attack at the moment.

## Requirements

- Python 2.7.x
- Wallaroo

## Generating Data

A data generator is bundled with the application.
For the default data set, including 10 seconds of normal load, 10 seconds of a DDoS attack load, and 10 seconds of normal tail load, execute

```bash
python data_gen.py
```

If you want to play around with different shapes of data, run

```bash
python data_gen.py --help
```

to see the avaiable tuning options.

## Running DDoS Detector

In a shell, start up the Metrics UI if you don't already have it running:

```bash
docker start mui
```

In a shell, set up a listener:

```bash
python receiver.py --host 127.0.0.1:7002
```

In another shell, set up your environment variables if you haven't already done so. Assuming you installed Machida according to the tutorial instructions you would do:

```bash
export PYTHONPATH="$PYTHONPATH:.:$HOME/wallaroo-tutorial/wallaroo/machida"
export PATH="$PATH:$HOME/wallaroo-tutorial/wallaroo/machida/build"
```

Run `machida` with `--application-module ddos_detector`:

```bash
machida --application-module ddos_detector --in 127.0.0.1:7010 \
  --out 127.0.0.1:7002   --control 127.0.0.1:12500 --data 127.0.0.1:12501 \
  --name initializer --cluster-initializer --worker-count 1 \
  --metrics 127.0.0.1:5001 --ponythreads 1 --ponypinasio --ponynoblock
```

In a third shell, send the log files using the specialised sender:

```bash
python sender.py --host 127.0.0.1:7010 --file data.json --batch 1000
```
