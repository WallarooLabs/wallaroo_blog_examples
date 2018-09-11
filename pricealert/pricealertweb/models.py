# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import datetime
from djmoney.models.fields import MoneyField

class MarketData(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now)
    type = models.CharField(max_length=200)
    price = MoneyField(max_digits=19, decimal_places=2, default_currency='USD')

class Alert(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    price = MoneyField(max_digits=19, decimal_places=2, default_currency='USD')
