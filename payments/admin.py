import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import TopUp


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    field_names = [field.name for field in opts.get_fields()]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_to_csv.short_description = "Download selected as .csv"

def invoice(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(reverse('payments:invoice_pdf', args=[obj.pk])))

class TopUpAdmin(admin.ModelAdmin):
    list_display = ['id', invoice, 'date_created', 'date_updated', 'user', 'amount', 'payment_intent_status', 'currency', 'live_mode']
    list_filter = ['id', 'date_created', 'date_updated', 'user', 'amount', 'payment_intent_status', 'currency', 'live_mode']
    actions = [export_to_csv]


admin.site.register(TopUp, TopUpAdmin)