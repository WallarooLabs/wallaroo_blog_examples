#!/usr/bin/env python2

"""
DDoS Detector Synthetic Data Generator

This script generates synthetic data for the Wallaroo DDoS Detection example.
The data is simplified, and has only four fields:
    1. timestamp: Timestamp, in the unix epoch format, with fractions of
       seconds
    2. client: Client IP string, in the 'a.b.c,d' format (user IP)
    3. server: Server IP string, in the 'a.b.c.d' format (server IP)
    4. resource: Target resource identifier string

The data is saved as serialized JSON, with newlines separating the records.

Execute

```bash
python data_gen.py --help
```

for a description of the tunable variables.
"""


import argparse
from itertools import imap, izip
import json
import random
import time


def gen_address_set(n, excl=set()):
    """
    Generate n IPv4 addresses, across the entire valid ip range, including
    the reserved address space.
    """
    addrs = set()
    while len(addrs) < n:
        addr = '{}.{}.{}.{}'.format(*[random.randint(1, 254)
                                      for x in range(4)])
        if addr not in excl:
            addrs.add(addr)
    return addrs


def gen_resource_set(n):
    """
    Generate n 10-character long resource identifiers.
    """
    res = set()
    while len(res) < n:
        res.add('{:10x}'.format(random.randrange(16**10)))
    return res


def weighted_random_choice_with_replacement(weights, values, n):
    """
    Select n items from a list with replacement using weights.

    The length of the `weights` list must be the same as the length
    of the `from` list.
    The sum of the weights should approximate to 1 (leaving room for floating
    point rounding errors, to keep things easy on the user).
    """
    # divide the range [0,1] to len(weights) segments, each the size of its
    # value.
    # e.g. transform each weight from weights[i] to sum(weights[:i+1])
    weighted_range = [sum(weights[:i+1]) for i in range(len(weights))]
    weighted_range[-1] = 1

    for c in xrange(n):
        v = random.random()
        # find which segment of the weighted range v is in, and select its
        # corresponding item from the selection list
        i = 0
        l = len(weighted_range)
        while i < l:
            if v > weighted_range[i]:
                i += 1
            else:
                break
        yield values[i]


def data_gen():
    parser = argparse.ArgumentParser(prog='DDoS Traffic Data Generator')

    parser.add_argument('--servers', type=int, default=100,
                        help='Number of servers')
    parser.add_argument('--resources', type=int, default=10000,
                        help='Number of resources')
    parser.add_argument('--clients', type=int, default=1000,
                        help='Number of clients')
    parser.add_argument('--attack-clients', type=int, default=10000,
                        help='Number of clients during an attack')
    parser.add_argument('--requests', type=int, default=1000,
                        help=('Number of requests per second of data during '
                              'normal load'))
    parser.add_argument('--attack-requests', type=int, default=10000,
                        help=('Number of requests per second of data during '
                              'a DDoS attack'))
    parser.add_argument('--duration', type=int, default=10,
                        help='Number of seconds to generate normal data for')
    parser.add_argument('--attack-duration', type=int, default=10,
                        help='Number of seconds to generate attack data for')
    parser.add_argument('--tail-duration', type=int, default=10,
                        help=('Number of seconds to generate normal tail data'
                              ' for'))
    parser.add_argument('--loaded-servers', type=int, default=10,
                        help='Number of servers under heavy load')
    parser.add_argument('--loaded-weight', type=float, default=0.75,
                        help=('Fraction of total load allocated to loaded'
                              ' servers'))
    parser.add_argument('--file', type=argparse.FileType('w'),
                        default='data.json',
                        help='File in which to write the output data')

    args = parser.parse_args()

    # Create a list of servers, resources, and clients
    print('creating {} server addresses'.format(args.servers))
    servers = gen_address_set(args.servers)
    print('creating {} client addresses'.format(args.clients))
    clients = gen_address_set(args.clients, servers)
    print('creating {} attack client addresses'.format(args.attack_clients))
    attack_clients = gen_address_set(args.attack_clients, servers)
    print('creating {} resources'.format(args.resources))
    resources = list(gen_resource_set(args.resources))
    print('sorting client addresses')
    clients = sorted(list(clients))
    print('sorting attack client addresses')
    attack_clients = sorted(list(attack_clients)*10 + list(clients))
    print('sorting server addresses')
    servers = sorted(list(servers))

    # total number of requests for each period
    n_normal = args.requests * args.duration
    n_attack = args.attack_requests * args.attack_duration
    n_tail = args.requests * args.tail_duration

    # base timestamp for each period
    normal_base_time = 1509494400  # 2017-11-01 00:00:00 UTC
    attack_base_time = normal_base_time + args.duration
    tail_base_time = attack_base_time + args.attack_duration

    #
    # Normal period data
    #
    print('Generating {} seconds of data for normal load period'
          .format(args.duration))
    t_frac = 1.0/args.requests
    req_times = imap(lambda x: normal_base_time + x*t_frac, xrange(n_normal))
    req_clients = imap(lambda x: random.choice(clients), xrange(n_normal))
    req_servers = imap(lambda x: random.choice(servers), xrange(n_normal))
    req_resources = imap(lambda x: random.choice(resources), range(n_normal))

    offset = args.file.tell()
    for tup in izip(req_times, req_clients, req_servers, req_resources):
        json.dump({'timestamp': tup[0], 'client': tup[1], 'server': tup[2],
                   'resource': tup[3]}, args.file, separators=(',', ':'))
        args.file.write('\n')
    mb_written = (args.file.tell() - offset) / (1024.0 * 1024.0)
    print("written {} MB to '{}' for a normal period of {} seconds"
          .format(mb_written, args.file.name, args.duration))

    #
    # Attack period data
    #
    print('Generating {} seconds of data for attack load period'
          .format(args.attack_duration))
    t_frac = 1.0/args.attack_requests
    req_times = imap(lambda x: attack_base_time + x*t_frac, xrange(n_attack))
    req_clients = imap(lambda x: random.choice(attack_clients),
                       xrange(n_attack))

    w_servers = ([args.loaded_weight/args.loaded_servers for x in xrange(5)] +
                 [(1-args.loaded_weight)/(len(servers)-args.loaded_servers)
                  for x in xrange(len(servers)-args.loaded_servers)])
    req_servers = weighted_random_choice_with_replacement(w_servers, servers,
                                                          n_attack)

    w_resources = ([0.90/10 for x in xrange(10)] +
                   [0.10/(len(resources)-10)
                    for x in xrange(len(resources)-10)])
    req_resources = weighted_random_choice_with_replacement(w_resources,
                                                            resources,
                                                            n_attack)

    offset = args.file.tell()
    for tup in izip(req_times, req_clients, req_servers, req_resources):
        json.dump({'timestamp': tup[0], 'client': tup[1], 'server': tup[2],
                   'resource': tup[3]}, args.file, separators=(',', ':'))
        args.file.write('\n')
    mb_written = (args.file.tell() - offset) / (1024.0 * 1024.0)
    print("written {} MB to '{}' for an attack period of {} seconds"
          .format(mb_written, args.file.name, args.duration))

    #
    # Tail period data
    #
    print('generating data for tail load period')
    t_frac = 1.0/args.requests
    req_times = imap(lambda x: tail_base_time + x*t_frac, xrange(n_tail))
    req_clients = imap(lambda x: random.choice(clients), xrange(n_tail))
    req_servers = imap(lambda x: random.choice(servers), xrange(n_tail))
    req_resources = imap(lambda x: random.choice(resources), range(n_tail))

    offset = args.file.tell()
    for tup in izip(req_times, req_clients, req_servers, req_resources):
        json.dump({'timestamp': tup[0], 'client': tup[1], 'server': tup[2],
                   'resource': tup[3]}, args.file, separators=(',', ':'))
        args.file.write('\n')
    mb_written = (args.file.tell() - offset) / (1024.0 * 1024.0)
    print("written {} MB to '{}' for a tail period of {} seconds"
          .format(mb_written, args.file.name, args.duration))

    mb_written = args.file.tell()
    print('Total data written: {} bytes'.format(mb_written))


if __name__ == '__main__':
    data_gen()
