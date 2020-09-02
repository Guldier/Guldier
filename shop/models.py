from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import calendar

class Dish(models.Model):
    name = models.CharField(max_length=100)
    ingredient = models.CharField(max_length=250, blank=True)
    price = models.FloatField()
    dish_type = models.CharField(max_length=20)
    dish_addon = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'

class AddOn(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    addon_type = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}'

class Composition(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    addon = models.ForeignKey(AddOn, on_delete=models.CASCADE)
    #price = models.FloatField()

    def __str__(self):
        if self.addon.name == 'empty':
            return f'{self.dish}'
        elif self.addon.addon_type == 'pizza':
            return f'{self.dish} - {self.addon}'
        else:
            return f'{self.dish} + {self.addon}'
        
class Orders(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    quantity = models.IntegerField()


    def __str__(self):
        return f'{self.user} + {self.composition} - {self.quantity}szt.'
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user} - {self.composition} - {self.quantity}szt.'


class WeekDish(models.Model):
    day = models.IntegerField()
    name = models.CharField(max_length=100)
    ingredient = models.CharField(max_length=250, blank=True)

    def __str__(self):
        days = list(calendar.day_name)
        return f'{days[self.day]} - {self.name} - {self.ingredient}'