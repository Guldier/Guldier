from django.contrib import admin
from .models import Profile,MoneyMovement

class MoneyAdminSearch(admin.ModelAdmin):
    search_fields = ['profile__user__username']

admin.site.register(Profile)
admin.site.register(MoneyMovement, MoneyAdminSearch)