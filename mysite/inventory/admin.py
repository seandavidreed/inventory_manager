from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Supplier, Item, Order

# Register your models here.
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'send_email', 'phone']

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['supplier', ('brand', 'unit')]
        }),
        ('Packaging', {
            'classes': ['collapse'],
            'fields': [('package', 'package_qty')]
        }),
        (None, {
            'fields': ['quota', 'storage']
        })
    ]
    list_display = ['__str__', 'supplier', 'quota', 'package']
    ordering = ['id']


class OrderAdmin(admin.ModelAdmin):
    fields = ('date', 'order_number', 'item', 'order_quantity')

admin.site.unregister(Group)
admin.site.register(Item, ItemAdmin)
admin.site.register(Supplier, SupplierAdmin)
