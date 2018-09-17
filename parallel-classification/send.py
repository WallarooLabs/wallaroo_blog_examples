#!/usr/bin/env python

import socket
import struct
import sys
opts = list()

hostport = sys.argv[1].split(":")
filename = sys.argv[2]
EOT="\x04"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (hostport[0], int(hostport[1]))
print('Sending {} to {!r}'.format(filename, server_address))
sock.connect(server_address)

try:
   with open(filename, 'rb') as f:
     for line in f.readlines():
       line = line.strip()
       sock.sendall(struct.pack(">I",len(line))+line)

finally:
   sock.sendall(struct.pack(">I",len(EOT))+EOT)
   print('Done sending {}'.format(filename))
   sock.close()
