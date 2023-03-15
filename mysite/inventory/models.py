from unicodedata import name
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length

from admin_ordering.models import OrderableModel

models.CharField.register_lookup(Length)

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=50, help_text='Example: Dillanos')
    email = models.EmailField(max_length=100)
    default_message = models.CharField(default='', max_length=250, help_text='Example: Here\'s our order for today. Thank you!')
    send_email = models.BooleanField(default=True, help_text='Set "True" if you want orders to be sent to supplier email')
    phone = models.CharField(max_length=20, help_text='Preferred format: 111-222-3333')

    def __str__(self):
        return self.name


class Item(OrderableModel):
    supplier = models.ForeignKey('Supplier', on_delete=models.DO_NOTHING)
    brand = models.CharField(max_length=50, blank=True, help_text='Example: Torani (Not Required)')
    unit = models.CharField(max_length=50, help_text='Example: Strawberry (required)')
    package = models.CharField(default='', blank=True, max_length=10, choices=[('box(es)', 'Box(es)'), ('case(s)', 'Case(s)'), ('carton(s)', 'Carton(s)'), ('pack(s)', 'Pack(s)')])
    package_qty = models.IntegerField(default=0, help_text='Quantity of unit per package')
    quota = models.IntegerField(default=0, help_text='The required minimum quantity when restocking has occurred')
    storage = models.CharField(max_length=2, choices=[('A', 'Shed'), ('B', 'Shop')])
    latest_qty = models.IntegerField(default=0, editable=False, help_text='The last quantity ordered')

    class Meta(OrderableModel.Meta):
        constraints = [
            models.CheckConstraint(
                check=(Q(package__length=0, package_qty=0) | Q(package__length__gt=0, package_qty__gt=0)), 
                name='packaging'
            )
        ]

    def __str__(self):
        return self.brand + ' ' + self.unit


class Order(models.Model):
    item = models.ForeignKey('Item', on_delete=models.DO_NOTHING)
    date = models.DateField()
    order_number = models.IntegerField(default=1, help_text='The unique value used to identify an order')
    order_qty = models.IntegerField(default=0, help_text='The amount of a given item to be ordered')

    def __str__(self):
        return str(self.date)