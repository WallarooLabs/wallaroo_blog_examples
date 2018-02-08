import sys
import socket
import struct
from sklearn import linear_model, decomposition, datasets

import cPickle as pickle

def send_message(conn, x):
    msg = pickle.dumps(x)
    conn.sendall(struct.pack('>I', len(msg)))
    conn.sendall(msg)

if __name__ == '__main__':
    add = sys.argv[1].split(':')
    wallaroo_input_address = (add[0], int(add[1]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'connecting to Wallaroo on %s:%s' % wallaroo_input_address
    sock.connect(wallaroo_input_address)
    digits = datasets.load_digits()
    for x in digits.data:
        send_message(sock, x)
