import string
import struct
import wallaroo

def application_setup(args):
    input_addrs = wallaroo.tcp_parse_input_addrs(args)
    
    ll_host, ll_port = input_addrs[0]
    cc_host, cc_port = input_addrs[1]

    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]

    initial_partitions = range(0,10)

    ab = wallaroo.ApplicationBuilder("Ad Tech Application")
    ab.new_pipeline("Load loyalty customers", 
        wallaroo.TCPSourceConfig(ll_host, ll_port, ll_decoder))
    ab.to_state_partition(save_customer, LoyaltyCustomers, 
        "loyalty customers", extract_conversion_key, initial_partitions)
    ab.done()
    
    ab.new_pipeline("Conversions",
        wallaroo.TCPSourceConfig(cc_host, cc_port, cc_decoder))
    ab.to_state_partition(process_email_add_customer, LoyaltyCustomers, 
        "loyalty customers", extract_conversion_key, initial_partitions)
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, cc_encoder))

    return ab.build()

class LoyaltyCustomers(object):
    def __init__(self):
        self.customers = {}
        
    def add(self, customer_email, loyaltycustomer):
        self.customers[customer_email]=loyaltycustomer
        
class Customer(object):
    def __init__(self, customer_email, fb_user, insta_user, gender):
        self.customer_email = customer_email
        self.fb_user = fb_user
        self.insta_user = insta_user
        self.gender = gender
        
class ClickConversion(object):
    def __init__(self, promo_ad, conversion, customer_email, where):
        self.promo_ad = promo_ad
        self.conversion = conversion
        self.customer_email = customer_email
        self.where = where

class BasketConversion(object):
    def __init__(self, promo_ad, conversion, customer_email, items):
        self.promo_ad = promo_ad
        self.conversion = conversion
        self.customer_email = customer_email
        self.items = items

class PurchaseConversion(object):
    def __init__(self, promo_ad, conversion, customer_email, items, total_cost):
        self.promo_ad = promo_ad
        self.conversion = conversion
        self.customer_email = customer_email
        self.items = items
        self.total_cost = total_cost

@wallaroo.partition
def extract_conversion_key(data):
    return hash(data.customer_email) % 10

@wallaroo.state_computation(name="save customers")
def save_customer(data, loyalty_customers):
    loyalty_customers.add(data.customer_email, data)
    return (None, True)

@wallaroo.state_computation(name="conversions")
def save_conversion(data, conversions):
    conversions.add(data)
    return (data, True)

@wallaroo.state_computation(name="add_new_loyalty_customer")
def process_email_add_customer(conversion, loyalty_customers):
    should_email = False
    if conversion.customer_email in loyalty_customers.customers:
        if conversion.conversion == 'ClickConversion':
            should_email = True
    else:
        if conversion.conversion == 'PurchaseConversion':
            loyalty_customers.add(conversion.customer_email,
                Customer(conversion.customer_email, '','',''))
    return ((conversion, should_email), True)

@wallaroo.decoder(header_length=4, length_fmt=">I")
def ll_decoder(data):
    print("decoding customer: " + data)
    info = data.split(",")
    return Customer(info[0].strip(), info[1].strip(),
                    info[2].strip(), info[3].strip())
    
@wallaroo.decoder(header_length=4, length_fmt=">I")
def cc_decoder(data):
    info = data.split(",")
    if info[1].strip() == 'ClickConversion':
        print("decoding click conversion: " + data)
        conversion = build_click_conversion(info)
    elif info[1].strip() == 'BasketConversion':
        print("decoding basket conversion: " + data)
        conversion = build_basket_conversion(info)
    elif info[1].strip() == 'PurchaseConversion':
        print("decoding purchase conversion: " + data)
        conversion = build_purchase_conversion(info)
    return conversion

def build_click_conversion(info):
    return ClickConversion(info[0].strip(), info[1].strip(),
                           info[2].strip(), info[3].strip())

def build_basket_conversion(info):
    return BasketConversion(info[0].strip(), info[1].strip(),
                            info[2].strip(), info[3].strip())

def build_purchase_conversion(info):
    return PurchaseConversion(info[0].strip(), info[1].strip(),
                              info[2].strip(), info[3].strip(), info[3].strip())
        
@wallaroo.encoder
def cc_encoder(data):
    (conversion, should_email) = data
    return ("Send additional promo code to: " + conversion.customer_email
            + ", " + str(should_email) + "\n")
