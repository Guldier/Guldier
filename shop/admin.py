from django.contrib import admin
from .models import Dish, AddOn, Composition, Chart

admin.site.register(Dish)
admin.site.register(AddOn)
admin.site.register(Composition)
admin.site.register(Chart)
# Register your models here.
