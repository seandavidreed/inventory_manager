from django.contrib import admin
from django.contrib.auth.models import Group

from admin_ordering.admin import OrderableAdmin

from .models import Supplier, Item

# Register your models here.
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'send_email', 'phone']

class ItemAdmin(OrderableAdmin, admin.ModelAdmin):
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
    ordering_field = "ordering"
    ordering_field_hide_input = "True"
    list_display = ['__str__', 'supplier', 'quota', 'package', 'ordering']
    list_editable = ["ordering"]
    list_per_page = 1000

class OrderAdmin(admin.ModelAdmin):
    fields = ('date', 'order_number', 'item', 'order_quantity')

admin.site.unregister(Group)
admin.site.register(Item, ItemAdmin)
admin.site.register(Supplier, SupplierAdmin)
