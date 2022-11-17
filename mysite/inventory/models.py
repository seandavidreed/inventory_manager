from unicodedata import name
from django.db import models

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=50, help_text='Example: Dillanos')
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20, help_text='Preferred format: 111-222-3333')

    def __str__(self):
        return self.name


class Item(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50, help_text='Example: Torani')
    unit = models.CharField(max_length=50, help_text='Example: Strawberry')
    quota = models.IntegerField(default=0, help_text='The required minimum quantity when restocking has occurred')
    storage = models.CharField(max_length=2, choices=[('A', 'Shed'), ('B', 'Shop')])
    upc_code = models.IntegerField(default=0, help_text='Store the unique 12-digit UPC code fetched from scanner')

    def __str__(self):
        return self.brand + ' ' + self.unit


class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    date = models.DateField()
    order_number = models.IntegerField(default=0, help_text='The unique value used to identify an order')
    order_qty = models.IntegerField(default=0, help_text='The amount of a given item to be ordered')

    def __str__(self):
        return str(self.date)