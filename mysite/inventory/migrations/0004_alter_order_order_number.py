# Generated by Django 4.1.3 on 2022-11-18 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_order_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.IntegerField(default=1, help_text='The unique value used to identify an order'),
        ),
    ]