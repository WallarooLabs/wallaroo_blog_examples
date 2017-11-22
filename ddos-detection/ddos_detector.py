import json
import pickle
import struct

import wallaroo

from circular_buffer import CircularBuffer
from stats import weighted_mu_sigma


def application_setup(args):
    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]

    partitions = 10000
    server_partitions = range(partitions)

    ab = wallaroo.ApplicationBuilder("DDoS Attack Detector")
    ab.new_pipeline("ddos detection",
                    wallaroo.TCPSourceConfig(in_host, in_port, Decoder()))
    ab.to_state_partition_u64(ProcessLogEntry(), PartitionStatsBuilder(),
                          "process log entry",
                          ServerPartitionFunction(partitions),
                          server_partitions)
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, Encoder()))
    return ab.build()


class Decoder(object):
    def header_length(self):
        return 4

    def payload_length(self, bs):
        return struct.unpack(">I", bs)[0]

    def decode(self, bs):
        return json.loads(bs)


class ServerPartitionFunction(object):
    def __init__(self, partitions):
        self.part_size = 2**32/partitions

    def partition(self, data):
        # Convert the server's ip address to a number and divide it by
        # the partition size. The result is the partition index.
        parts = data['server'].split('.')
        ipnum = ((int(parts[0]) << 24) + (int(parts[1]) << 16) +
                 (int(parts[2]) << 8) + int(parts[3]))
        return ipnum/self.part_size


class PartitionStatsBuilder(object):
    def build(self):
        return PartitionLoadStatistics()


class PartitionLoadStatistics(object):
    def __init__(self):
        self.servers = {}

    def update(self, data):
        return (self.servers.setdefault(data['server'],
                                        SingleServerLoadStatistics(
                                            data['server']))
                .update(data))


class SingleServerLoadStatistics(object):
    """
    An object for keeping and updating the statistics of a server.

    In here we meintain:
        - a circular buffer of size 60, with tuples of:
            - unix epoch timestamp
            - requests / second
            - unique clients / second
        - requests for the current fragment
        - set of unique client IPs for current fragment
        - current fragment timestamp

    There are two types of updates:
        1. update to in-progress second
        2. update to circular buffer

    Each message in the wallaroo stream results in type 1.
    When a message in the stream has a timestamp that is greater than the
    current fragment timestamp, this is used as an indicator to
    store the current fragment values into the circular buffer, and start
    new ones for the new fragment timestamp.
    If there is a gap between the new timestamp and the previous one, then we
    fill it up with (timestamp, 0, 0) tuples, assuming there was no traffic
    for that period.
    """

    def __init__(self, address):
        self.address = address
        self.window = CircularBuffer(60)  # Store last 60 seconds of traffic stats
        self.requests_mean = 0
        self.requests_stdev = 0
        self.clients_mean = 0
        self.clients_stdev = 0
        # Store current second of traffic stats:
        self.current_ts = 0
        self.current_requests = 0
        self.current_clients = set()
        self.is_attack = False

    def update_fragment(self, data):
        self.current_requests += 1
        self.current_clients.add(data['client'])

    def update_model(self, timestamp):
        if not self.window:
            # if the window is empty, don't bother backfilling
            self.window.append((self.current_ts, self.current_requests,
                                len(self.current_clients)))
            self.requests_mean = self.current_requests
            self.clients_mean = len(self.current_clients)
        else:
            # Ugh. I guess we have to do actual work now!
            last_ts = self.window[-1][0]
            for ts in range(last_ts, self.current_ts):
                self.window.append((ts, 0, 0))
            self.window.append((self.current_ts, self.current_requests,
                                len(self.current_clients)))

            # repeat the same thing for the difference between
            # current_timestamp and the usurping timesamp
            last_ts = self.window[-1][0]
            for ts in range(last_ts, timestamp):
                self.window.append((ts, 0, 0))

            # Update the means and sigmas, but only if not under attack!
            if not self.is_attack:
                self.requests_mean, self.requests_stdev = (
                    weighted_mu_sigma(map(lambda x: x[2], self.window),
                                      range(1, len(self.window) + 1)))
                self.clients_mean, self.clients_stdev = (
                    weighted_mu_sigma(map(lambda x: x[1], self.window),
                                      range(1, len(self.window) + 1)))

        # And finally, reset the in-progress values
        self.current_ts = timestamp
        self.current_requests = 0
        self.current_clients = set()

    def predict_from_fragment(self, timestamp):
        # predict whether current fragment's status is "under attack" or not
        # Note that we don't want to start predicting _too_ early here, or
        # else we'll get very unstable numbers.
        # We can check the number of clients and requests is over a threshold
        # before making any assessments.
        ts_frac = timestamp % 1
        if ts_frac > 0 and self.current_requests > 10:
            # compute the expected final value for the current aggregator
            exp_cli = len(self.current_clients)/ts_frac
            exp_req = self.current_requests/ts_frac

            # is it >2sigma from the mean?
            is_attack = False
            if (exp_cli - self.clients_mean) > (2 * self.clients_stdev):
                is_attack = True
            elif (exp_req - self.requests_mean) > (2 * self.requests_stdev):
                is_attack = True

            if is_attack:
                if self.is_attack:
                    # under_attack -> under_attack
                    return None
                else:
                    if self.current_requests > 20:
                        # healthy -> under_attack
                        self.is_attack = True
                        return (self.address, timestamp, True)
            else:
                if self.is_attack:
                    # under_attack -> healthy
                    self.is_attack = False
                    return (self.address, timestamp, False)
                else:
                    # healthy -> healthy
                    return None
        # not enough data, so nothing else to do

    def update(self, data):
        # update model if necessary
        if int(data['timestamp']) > self.current_ts:
            if self.current_ts == 0:
                self.current_ts = int(data['timestamp'])
            else:
                self.update_model(int(data['timestamp']))

        # update the current fragment
        self.update_fragment(data)

        # predict status and return the result
        return self.predict_from_fragment(data['timestamp'])



class ProcessLogEntry(object):
    def name(self):
        return "Process web log entry"

    def compute(self, data, state):
        status = state.update(data)
        return (status, True)


class Encoder(object):
    def encode(self, data):
        # data is a tuple of (server_name, timestamp, is_under_attack)
        if data[2]:
            # under attack
            out = ("Server {} is under ATTACK! (Status changed at {})"
                   .format(data[0], data[1]))
        else:
            # no longer under attack
            out = ("Server {} is no longer under attack. "
                   "(Status changed at {})"
                   .format(data[0], data[1]))
        return struct.pack(">I{}s".format(len(out)), len(out), out)
