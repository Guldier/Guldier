from django.contrib import admin
from .models import Dish, AddOn, Composition, Cart, Orders, WeekDish

class WeekDishAdmin(admin.ModelAdmin):
    search_fields = ['day']

admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
admin.site.register(Cart)
admin.site.register(Orders)
admin.site.register(WeekDish,WeekDishAdmin)
# Register your models here.
