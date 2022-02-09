import weasyprint
from io import BytesIO

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator, MinLengthValidator
from django.template.loader import render_to_string

from users.models import Profile

mail_sender = settings.DEFAULT_FROM_EMAIL

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

    def write_invoice_to_pdf(self, target):
        html = render_to_string('payments/invoice_pdf.html', {'topup': self})
        weasyprint.HTML(string=html).write_pdf(target)
        return target

    def send_email_with_invoice(self):
        subject = f'Guldier - invoice no. {self.pk}'
        message = 'Thank you for choosing our service. Attached you will find an invoice.'
        email = EmailMessage(subject=subject, body=message, from_email=mail_sender, to=[self.user.email])
        out = BytesIO()
        self.write_invoice_to_pdf(out)
        email.attach(filename='invoice_{}.pdf'.format(self.pk), content=out.getvalue(), mimetype='application/pdf')
        email.send()


class Address(models.Model):

    def only_numbers_validator(value):
        if not value.isdigit():
            message = '"{}" is not a valid postal code'.format(value)
            raise ValidationError(message=message)

    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # on delete cascade - czy slusznie? w topup ta sama watpliwosc. utrata danych
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    street_and_number = models.CharField(max_length=256)
    city = models.CharField(max_length=128)
    country = models.CharField(max_length=1280)
    postal_code = models.CharField(max_length=5, validators=[only_numbers_validator])

    def __str__(self, *args, **kwargs):
        return '{} {}, {} {} {}, {}'.format(
            self.name,
            self.surname,
            self.street_and_appartment,
            self.postal_code,
            self.city,
            self.country
        )


class Invoice(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    topup = models.ForeignKey(TopUp, on_delete=models.CASCADE)

    def save_name(self, *args, **kwargs):
        self.name = 'G/{}/{}/{}'.format(
            self.pk, 
            '{:02d}'.format(self.date_created.month), 
            self.date_created.year
            )
        super().save(*args, **kwargs)
