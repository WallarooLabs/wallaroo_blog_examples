import argparse
import json
import socket
import struct
import time


parser = argparse.ArgumentParser(prog='DDoS Traffic sender')
parser.add_argument('--host', type=str, help="e.g. 127.0.0.1:5000")
parser.add_argument('--batch-size', type=int, default=100)
parser.add_argument('--file', type=argparse.FileType('r'))

args = parser.parse_args()
host, port = (lambda x,y: (x, int(y)))(*(args.host.split(':')))

# open socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

t = time.time()
c = 0
while True:
    t0 = time.time()
    # read up to 100 lines
    lines = [s for s in
             (args.file.readline() for x in range(args.batch_size))
             if s]
    c += len(lines)
    if not lines:
        break
    if len(lines) > 1:
        lines_dt = (json.loads(lines[-1])['timestamp'] -
                    json.loads(lines[0])['timestamp'])
    else:
        lines_dt = 0

    # construct single bytestring for total batch
    to_send = ''.join((struct.pack('>I{}s'.format(l), l, s)
                       for l,s in zip(map(len, lines), lines)))
    sock.sendall(to_send)
    dt = time.time() - t0
    to_sleep = max(0, (lines_dt - dt))
    print('sent {} bytes of data for {} records. Sleeping for {} seconds'
          .format(len(to_send), len(lines), to_sleep))
    time.sleep(to_sleep)
sock.close()
args.file.close()

print()
print('Sent {} records in {} seconds'.format(c, time.time()-t))

