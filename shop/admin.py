from django.contrib import admin
from .models import Dish, AddOn, Composition

admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
# Register your models here.
