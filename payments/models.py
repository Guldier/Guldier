from django.db import models


class Price(models.Model):
    stripe_id = models.CharField(max_length=32)
    # unit_amount = models.IntegerField(default=0)
    # currency = models.CharField(max_length=3)

    # def get_display_price(self):
    #     return "{0:.2f}".format(self.unit_amount / 100)