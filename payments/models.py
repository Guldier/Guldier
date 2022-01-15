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
    checkout_session_id = models.CharField(max_length=250, blank=True)
    checkout_session_body = models.TextField(blank=True)
    checkout_session_status = models.TextField(blank=True)
    #details taken from payment_intent object
    payment_intent_id = models.CharField(max_length=250, blank=True)
    payment_intent_body = models.TextField(blank=True)
    payment_intent_status = models.TextField(blank=True)
    # details taken from charge object
    charge_id = models.CharField(max_length=250, blank=True)
    charge_body = models.TextField(blank=True)
    charge_status = models.TextField(blank=True)
    # details taken from customer object
    customer_id = models.CharField(max_length=250, blank=True)
    customer_body = models.TextField(blank=True)
    customer_email = models.EmailField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    #details taken from payment_intent.created event
    currency = models.TextField(blank=True)
    amount = models.IntegerField(blank=True)
    live_mode = models.BooleanField(blank=True)
    # amount_intent_payment = models.IntegerField(default=0)
    # amount_from_stripe = models.IntegerField(null=True)
    # currency = models.CharField(default='pln', max_length=3)
    # date_intent_payment = models.DateTimeField(auto_now_add=True)
    # date_updated = models.DateTimeField(auto_now=True)
    # payment_status = models.CharField(max_length=10, choices=STATUS, default='new')
    # STATUS = Choices('new', 'pending', 'success', 'reject')
    # status = StatusField()