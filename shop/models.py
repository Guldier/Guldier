from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Dish(models.Model):
    name = models.CharField(max_length=100)
    ingredient = models.CharField(max_length=250)
    price = models.FloatField()
    dish_type = models.CharField(max_length=20)

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

    def __str__(self):
        return f'{self.dish} + {self.addon}'
        
class Orders(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)

class Chart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)