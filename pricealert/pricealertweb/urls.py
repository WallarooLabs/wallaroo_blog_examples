from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from pricealertweb.alert import views

urlpatterns = [
    url(r'^$', login_required(views.AlertView.as_view())),
    url(r'^new/', login_required(views.CreateAlertView.as_view()), name="alert_new"),
]
