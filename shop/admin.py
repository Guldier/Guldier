from django.contrib import admin
from .models import Dish, AddOn, Composition, Cart, Orders



admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
admin.site.register(Cart)
admin.site.register(Orders)
# Register your models here.
