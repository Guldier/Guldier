from django.contrib import admin
from .models import Dish, AddOn, Composition, Cart, Orders, WeekDish

class WeekDishAdmin(admin.ModelAdmin):
    list_display = ('day', 'name')
    search_fields = ('day', 'name')
    list_filter = ('day')


admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
admin.site.register(Cart)
admin.site.register(Orders)
admin.site.register(WeekDish,WeekDishAdmin)
# Register your models here.
