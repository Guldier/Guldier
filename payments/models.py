from django.db import models
from users.models import Profile
from django.contrib.auth.models import User



class Price(models.Model):
    stripe_id = models.CharField(max_length=32)
    # unit_amount = models.IntegerField(default=0)
    # currency = models.CharField(max_length=3)
    # def get_display_price(self):


class TopUp(models.Model):
    STATUS = [
        ('new', 'new'),
        ('pending', 'pending'),
        ('success', 'success'),
        ('reject', 'reject')
    ]

    amount_intent_payment = models.IntegerField(default=0)
    amount_from_stripe = models.IntegerField(null=True)
    currency = models.CharField(default='pln', max_length=3)
    date_intent_payment = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=10, choices=STATUS, default='new')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

