#!/usr/bin/env python
""" Usage:

./send.py 127.0.0.1:7777 file.csv

OR

./send.py 127.0.0.1:7777 --lines N
"""

import socket
import struct
import sys
import time
from generate_input_data import header_row, gen_row

EOT="\x04"
LINES_ARG="--lines"

hostport = sys.argv[1].split(":")
source = sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (hostport[0], int(hostport[1]))
sock.connect(server_address)

if source == LINES_ARG:
   n_lines = int(sys.argv[3])
   print('Generating {} lines + header, kill process to stop.'.format(n_lines))
   idx = 0
   header = ",".join(header_row())
   sock.sendall(struct.pack(">I",len(header))+header)
   while True:
      line = ",".join([str(field) for field in gen_row(idx)])
      sock.sendall(struct.pack(">I",len(line))+line)
      idx += 1
      if idx == n_lines:
         print('Generated {} lines + header, finalizing.'.format(n_lines))
         sock.sendall(struct.pack(">I",len(EOT))+EOT)
         sys.exit(0)
else:
   try:
      with open(source, 'rb') as f:
         print('Sending {} to {!r}'.format(source, server_address))
         for line in f.readlines():
            line = line.strip()
            sock.sendall(struct.pack(">I",len(line))+line)

   finally:
      sock.sendall(struct.pack(">I",len(EOT))+EOT)
      print('Done sending {}'.format(source))
      sock.close()
