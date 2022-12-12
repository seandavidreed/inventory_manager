# Generated by Django 4.1.3 on 2022-12-11 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_item_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(blank=True, help_text='Example: Torani (Not Required)', max_length=50),
        ),
        migrations.AlterField(
            model_name='item',
            name='package',
            field=models.CharField(blank=True, choices=[('box(es)', 'Box(es)'), ('case(s)', 'Case(s)'), ('carton(s)', 'Carton(s)'), ('pack(s)', 'Pack(s)')], default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(help_text='Example: Strawberry (required)', max_length=50),
        ),
    ]