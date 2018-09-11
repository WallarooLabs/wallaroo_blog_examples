from channels import Group
from datetime import datetime, timedelta
from django.db.models import Avg
from django.conf import settings
from djmoney.money import Money
from pricealert.celery import app
from pricealertweb.models import MarketData, Alert

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    if settings.WITH_WALLAROO == 'False':
        sender.add_periodic_task(10.0, notify_on_price.s(), name='Alert every 30')

def calculate_average_price():
    avg_price = MarketData.objects.filter(
        created_at__gte=datetime.now() - timedelta(minutes=10)
    ).aggregate(
        Avg('price')
    ).values()[0]
    return Money(avg_price, 'USD')

def get_alerts(avg_price):
    return Alert.objects.filter(
        price__lte=avg_price
    ).exclude(
        sent=True
    )

@app.task(ignore_result=True)
def notify_users(user_ids, price_set, avg_price):
    for user_id in user_ids:
        notify_user(user_id, price_set, avg_price)

def notify_user(user_id, price_set, avg_price):
    Group("user-{}".format(user_id)).send(
        {'text': "The current price of BTC is: %s has surpassed: %s" % (avg_price, price_set)}, immediately=True)
    return True

# This function is needed because otherwise we wouldn't be able to make the alert as sent
@app.task(ignore_result=True)
def mark_alert_as_sent(user_ids, alert_price):
    Alert.objects.filter(
        price=alert_price,
        user_id__in=user_ids
    ).update(sent=True)

@app.task(ignore_result=True)
def notify_on_price():
    avg_price = calculate_average_price()
    alerts = get_alerts(avg_price)
    for alert in alerts:
        notify_user(alert.user_id, alert.price, avg_price)
    alerts.update(sent=True)
    return True
