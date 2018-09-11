from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from pricealertweb.models import Alert, MarketData
import json
import struct

class AlertView(ListView):
    model = Alert
    context_object_name = 'alert_list'
    template_name = "alert/index.html"

    def get_queryset(self):
        return Alert.objects.filter(user_id__exact=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(AlertView, self).get_context_data(**kwargs)
        context['last_price'] = MarketData.objects.last().price
        return context

class CreateAlertView(CreateView):
    model = Alert
    template_name = "alert/new.html"
    fields = ['price']
    success_url = "/pricealert/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateAlertView, self).form_valid(form)

    @receiver(post_save, sender=Alert)
    def after_save_send_to_wallaroo(sender, instance, **kwargs):
        if settings.WITH_WALLAROO == 'True':
            message = json.dumps(dict({'price': str(instance.price.amount), 'user_id': instance.user_id}))
            settings.TCP_CONNECTION.sendall(struct.pack(">I",len(message))+message)
