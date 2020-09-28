from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money = models.FloatField(default=0)

    def __str__(self):
            return f'{self.user.username} Profile'


class MoneyMovement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    moneyMove = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.profile.user} - {self.moneyMove} - {self.date}'