import argparse
import socket
import struct
import threading
import time


class SingleSocketReceiver(threading.Thread):
    def __init__(self, sock, name):
        super(SingleSocketReceiver, self).__init__()
        self.daemon = True
        self.sock = sock
        self.header_fmt = '>I'
        self.header_length = struct.calcsize(self.header_fmt)
        self.name = name
        self.event = threading.Event()

    def run(self):
        while not self.event.is_set():
            header = self.sock.recv(self.header_length)
            if not header:
                self.stop()
                continue
            expect = struct.unpack(self.header_fmt, header)[0]
            data = self.sock.recv(expect)
            if not data:
                self.stop()
            else:
                print '{}: {}'.format(self.name, data)
                time.sleep(0.000001)

    def stop(self):
        self.event.set()
        self.sock.close()


class TCPReceiver(threading.Thread):
    def __init__(self, host, port):
        """
        Listen on a (host, port) pair.
        Each connection is handled by a separate client thread.
        """
        super(TCPReceiver, self).__init__()
        self.daemon = True
        self.event = threading.Event()
        self.host = host
        self.port = port
        self.max_connections = 100
        # Create a socket and start listening
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.max_connections)
        self.host, self.port = self.sock.getsockname()
        while not self.event.is_set():
            (clientsocket, address) = self.sock.accept()
            cl = SingleSocketReceiver(clientsocket,
                                      name = 'Receiver-{}'.format(
                                          len(self.clients)))
            print("TCPReceiver accepting connection from ({}, {}) on "
                  "port {}."
                  .format(self.host,
                   self.port, address[1]))
            self.clients.append(cl)
            cl.start()

    def stop(self):
        self.event.set()
        self.sock.close()
        for cl in self.clients:
            cl.stop()


parser = argparse.ArgumentParser(prog='DDoS Alert Receiver')
parser.add_argument('--host', type=str, help="e.g. 127.0.0.1:5000")

args = parser.parse_args()
host, port = (lambda x,y: (x, int(y)))(*(args.host.split(':')))

print("Starting a TCPReceiver listening on ({}:{})".format(host, port))
receiver = TCPReceiver(host, port)
receiver.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("KeyboardInterrupt received. Attempting clean shutdown...")
    receiver.stop()
    receiver.join(1)
