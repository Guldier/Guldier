import csv

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse

from .models import TopUp


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    field_names = [field.name for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_to_csv.short_description = "Download selected as .csv"


class TopUpAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_created', 'date_updated', 'user', 'amount', 'payment_intent_status', 'currency', 'live_mode']
    list_filter = ['id', 'date_created', 'date_updated', 'user', 'amount', 'payment_intent_status', 'currency', 'live_mode']
    actions = [export_to_csv]


admin.site.register(TopUp, TopUpAdmin)