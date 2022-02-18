from django.contrib import admin

from .models import TopUp, ToUpValueAndDiscount, Promotion


class DiscountAndPriceAdmin(admin.ModelAdmin):
    list_display = ('top_up_value', 'discount', 'promotion')


class PromotionDisp(admin.ModelAdmin):
    list_display = ('name', 'is_on', 'start_date', 'end_date')


admin.site.register(TopUp)
admin.site.register(Promotion, PromotionDisp)
admin.site.register(ToUpValueAndDiscount, DiscountAndPriceAdmin)
