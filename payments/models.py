from django.db import models
from django.contrib.auth.models import User
from users.models import Profile


class Price(models.Model):
    stripe_id = models.CharField(max_length=32)


class TopUp(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    #details taken from checkout.session object
    checkout_session_id = models.CharField(max_length=250, blank=True)
    checkout_session_status = models.CharField(max_length=50, blank=True)
    #details taken from payment_intent object
    payment_intent_id = models.CharField(max_length=250, blank=True)
    payment_intent_status = models.CharField(max_length=50, blank=True)
    # details taken from charge object
    charge_id = models.CharField(max_length=250, blank=True)
    charge_status = models.CharField(max_length=50, blank=True)
    # details taken from customer object
    customer_email = models.EmailField(null=True)
    #details taken from payment_intent.created event
    currency = models.CharField(max_length=3, blank=True)
    amount = models.IntegerField(null=True)
    live_mode = models.BooleanField(null=True)

    def __str__(self, *args, **kwargs):
        return self.pk