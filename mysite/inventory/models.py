from unicodedata import name
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length

models.CharField.register_lookup(Length)

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=50, help_text='Example: Dillanos')
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20, help_text='Preferred format: 111-222-3333')

    def __str__(self):
        return self.name


class Item(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)
    brand = models.CharField(max_length=50, help_text='Example: Torani')
    unit = models.CharField(max_length=50, help_text='Example: Strawberry')
    package = models.CharField(default='', blank=True, max_length=4, choices=[('BX', 'Box(es)'), ('C', 'Case(s)'), ('CRT', 'Carton(s)')])
    package_qty = models.IntegerField(default=0, help_text='Quantity of unit per package')
    quota = models.IntegerField(default=0, help_text='The required minimum quantity when restocking has occurred')
    storage = models.CharField(max_length=2, choices=[('A', 'Shed'), ('B', 'Shop')])
    latest_qty = models.IntegerField(default=0, editable=False, help_text='The last quantity ordered')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(Q(package__length__lt=1, package_qty__lt=1) | Q(package__length__gt=0, package_qty__gt=0)), 
                name='packaging'
            )
        ]

    def __str__(self):
        return self.brand + ' ' + self.unit


class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    date = models.DateField()
    order_number = models.IntegerField(default=1, help_text='The unique value used to identify an order')
    order_qty = models.IntegerField(default=0, help_text='The amount of a given item to be ordered')

    def __str__(self):
        return str(self.date)