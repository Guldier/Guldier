from django.contrib import admin

from .models import TopUp, ToUpValueAndDiscount


class DiscountAndPriceAdmin(admin.ModelAdmin):
    list_display = ('top_up_value', 'discount')


admin.site.register(TopUp)
admin.site.register(ToUpValueAndDiscount, DiscountAndPriceAdmin)
