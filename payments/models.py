from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from users.models import Profile

from datetime import date


class TopUpDateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-date_updated')


class TopUp(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # details taken from checkout.session object
    checkout_session_id = models.CharField(max_length=250, blank=True)
    checkout_session_status = models.CharField(max_length=50, blank=True)
    # details taken from payment_intent object
    payment_intent_id = models.CharField(max_length=250, blank=True)
    payment_intent_status = models.CharField(max_length=50, blank=True)
    # details taken from charge object
    charge_id = models.CharField(max_length=250, blank=True)
    charge_status = models.CharField(max_length=50, blank=True)
    # details taken from payment_intent.created event
    currency = models.CharField(max_length=3, blank=True)
    amount = models.IntegerField(null=True, validators=[MinValueValidator(15)])
    live_mode = models.BooleanField(null=True)
    payments = TopUpDateManager()
    objects = models.Manager()

    def __str__(self, *args, **kwargs):
        return str(self.pk)

    @property
    def amount_full_units(self):
        if self.amount:
            return f'{self.amount / 100:.2f}'


class Promotion(models.Model):
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    is_percent = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    active_dates = models.ForeignKey('PromotionDateRange', related_name='active_dates',
                                     on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.name} zniżka {self.discount}' + ('%' if self.is_percent else 'zł')


class Price(models.Model):
    amount = models.IntegerField()
    promotion = models.ForeignKey(Promotion, related_name='promotion', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.amount}'

    @property
    def get_discounted_price(self):

        if self.promotion.is_percent:
            return float(self.amount - self.amount * self.promotion.discount / 100)
        return self.amount - self.promotion.discount


class PromotionDateRange(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}: {self.start_date} - {self.end_date}'

    @property
    def date_within_range(self):
        """Checking if today`s date is between promotion start and end date"""
        return True if self.start_date <= date.today() <= self.end_date else False
