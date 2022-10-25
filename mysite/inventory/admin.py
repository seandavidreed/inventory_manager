from django.contrib import admin

from .models import Supplier, Item, Order

# Register your models here.
admin.site.register(Item)
admin.site.register(Supplier)
admin.site.register(Order)
