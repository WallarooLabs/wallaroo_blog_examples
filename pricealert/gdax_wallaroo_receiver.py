import socket
import requests
import ast
import django

# This is needed because we are running this outside of django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricealert.settings")
django.setup()

from pricealert.tasks import send_to_users, mark_alert_as_sent


def send_to_user(user_ids, alert_price, avg_price):
    notify_users(user_ids, alert_price, avg_price)

TCP_IP = "localhost"
TCP_PORT = 5555
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Waiting for data....")

while True:
    data = conn.recv(5000)
    if not data:
        print("no data received")
        break
    alert_json = json.loads(data)
    for (alert_price, user_ids) in alert_json.iteritems():
        if alert_price != 'average_price':
            send_to_users(user_ids, alert_price, alert_json["average_price"])
            mark_alert_as_sent(user_ids, alert_price)
