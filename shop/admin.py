from django.contrib import admin
from .models import Dish, AddOn, Composition, Cart

admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
admin.site.register(Cart)
# Register your models here.
