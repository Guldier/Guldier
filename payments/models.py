from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from model_utils.fields import StatusField
from model_utils import Choices
from users.models import Profile


class Price(models.Model):
    stripe_id = models.CharField(max_length=32)
    # unit_amount = models.IntegerField(default=0)
    # currency = models.CharField(max_length=3)
    # def get_display_price(self):


class TopUp(models.Model):
    #auto-populated fields for tracking date of creation and update of a payment from the customer
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    #internal payment ID
    payment_id = models.AutoField(primary_key=True)

    #details taken from checkout.session object
    checkout_session_id = models.CharField(max_length=250, null=True)
    checkout_session_body = models.TextField(null=True)
    checkout_session_status = models.TextField(null=True)
    #details taken from payment_intent object
    payment_intent_id = models.CharField(max_length=250, null=True)
    payment_intent_body = models.TextField(null=True)
    payment_intent_status = models.TextField(null=True)
    # details taken from charge object
    charge_id = models.CharField(max_length=250, null=True)
    charge_body = models.TextField(null=True)
    charge_status = models.TextField(null=True)
    # details taken from customer object
    customer_email = models.EmailField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    #details taken from payment_intent.created event
    currency = models.CharField(max_length=3, null=True)
    amount = models.IntegerField(null=True)
    live_mode = models.BooleanField(null=True)

    def __str__(self, *args, **kwargs):
        return f'Transaction no. {self.payment_id}'