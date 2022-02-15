from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from users.models import Profile


class TopUpDateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-date_updated')


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
    #details taken from payment_intent.created event
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


class ToUpValueAndDiscount(models.Model):
    top_up_value = models.PositiveSmallIntegerField()
    discount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.top_up_value}'
