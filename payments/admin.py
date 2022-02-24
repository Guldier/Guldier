from django.contrib import admin

from .models import TopUp, Price, Promotion, PromotionDateRange


class PriceAdmin(admin.ModelAdmin):
    list_display = ('amount', 'promotion')


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'discount', 'is_percent', 'notes', 'active_dates')


class DatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')


admin.site.register(TopUp)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(PromotionDateRange)
