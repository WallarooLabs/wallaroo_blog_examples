import socket
import requests
import ast

TCP_IP = "localhost"
TCP_PORT = 7002
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Waiting for data....")

buffer = ""
while True:
    data = conn.recv(5000)
    if not data:
        print("no data received")
        break
    buffer += data
    while True:
        # check if the separator doesn't exist then continue fetching data from network to the buffer
        if ';;' not in buffer:
            break
        # split the buffer data by the separator to extract the full complete data
        # and put the remaining text again in the buffer
        full_message, separator, buffer = buffer.partition(';;')

        # initialize and send the data through REST API
        url = 'http://localhost:5003/updateDashboard'

        # replace some escaping characters that have been added to the data while conversion
        full_message = full_message.replace("\'","'").replace("\\\\","\\")
        # send the data to the RESTful Webservice as a dictionary
        response = requests.post(url, data=ast.literal_eval(full_message))
