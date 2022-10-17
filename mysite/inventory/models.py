from unicodedata import name
from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the full name of the item')
    brand = models.CharField(max_length=50, help_text='Example: Torani')
    unit = models.CharField(max_length=50, help_text='Example: Strawberry')
    par = models.IntegerField(default=0, help_text='The required minimum quantity when restocking has occurred')
    current_qty = models.IntegerField(default=0, help_text='The actual amount available prior to ordering')
    upc_code = models.IntegerField(default=0, help_text='Store the unique 12-digit UPC code fetched from scanner')

    def __str__(self):
        return self.name