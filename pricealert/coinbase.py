import json
import struct
import decimal
import wallaroo

def application_setup(args):
    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]
    ll_host, ll_port = wallaroo.tcp_parse_input_addrs(args)[1]
    ab = wallaroo.ApplicationBuilder("gdax alerts")
    # Pipeline to store alerts and the corresponding user
    ab.new_pipeline("Load users created alerts",
                    wallaroo.TCPSourceConfig(ll_host, ll_port, decoder))
    ab.to_stateful(save_alert, Alerts, "user set alerts")
    ab.done()

    # Pipeline to calculate current bitcoin price from gdax
    ab.new_pipeline("Average BTC price",
                    wallaroo.TCPSourceConfig(in_host, in_port, decoder))
    ab.to_parallel(extract_price)
    # State object, current_price
    # Update the moving
    ab.to_stateful(calculate_and_update_average_price, BTCPrice,
                   "Calculate and update the average price")
    # Alerts are map of `price: [user_ids]`
    # Alert.update lookup users, return and replace with None
    # Send to another application, that then calls a cellery task
    ab.to_stateful(maybe_send_alerts_based_on_average_price,
                   Alerts, "user set alerts")
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, encoder))
    return ab.build()

# To save the alerts
class Alerts(object):
    def __init__(self):
        self.alerts = dict()

    def add(self, alert_price, user_id):
        old_value = self.alerts.get(alert_price, set([]))
        self.alerts[alert_price] = old_value.union(set([user_id]))

    def remove(self, alert_price):
        self.alerts.pop(alert_price, None)

class BTCPrice(object):
    def __init__(self):
        self.count = 0
        self.total = decimal.Decimal()
        self.average = decimal.Decimal()


@wallaroo.state_computation(name="save alert")
def save_alert(data, alerts):
    alerts.add(data['price'], data['user_id'])
    return (None, True)


@wallaroo.computation(name="extract price")
def extract_price(data):
    return (data["price"], True)


@wallaroo.state_computation(name="calculate and update the average price")
def calculate_and_update_average_price(price, btc_price):
    btc_price.total = decimal.Decimal(price[0]) + btc_price.total
    btc_price.count += 1
    btc_price.average = btc_price.total / btc_price.count
    return (btc_price, True)


@wallaroo.state_computation(name="maybe send notification")
def maybe_send_alerts_based_on_average_price(btc_price, alerts):
    notify = {}
    for (k,v) in alerts.alerts.items():
        if decimal.Decimal(k) <= btc_price.average:
            notify[k] = list(v)
            alerts.remove(k)

    if notify:
        notify["average_price"] = str(btc_price.average)
        return (notify, True)
    return (None, False)


@wallaroo.decoder(header_length=4, length_fmt=">I")
def decoder(data):
    json_data = json.loads(data.decode("utf-8"))
    return json_data


@wallaroo.encoder
def encoder(data):
    output = json.dumps(data)
    payload = bytes(output)
    return payload
