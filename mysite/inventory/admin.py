from django.contrib import admin

from .models import Supplier, Item, Order

# Register your models here.
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


admin.site.register(Item, ItemAdmin)
admin.site.register(Supplier)
# admin.site.register(Order)
