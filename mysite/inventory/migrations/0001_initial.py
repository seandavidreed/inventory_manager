# Generated by Django 4.1.3 on 2023-03-13 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField(default=0, verbose_name='ordering')),
                ('brand', models.CharField(blank=True, help_text='Example: Torani (Not Required)', max_length=50)),
                ('unit', models.CharField(help_text='Example: Strawberry (required)', max_length=50)),
                ('package', models.CharField(blank=True, choices=[('box(es)', 'Box(es)'), ('case(s)', 'Case(s)'), ('carton(s)', 'Carton(s)'), ('pack(s)', 'Pack(s)')], default='', max_length=10)),
                ('package_qty', models.IntegerField(default=0, help_text='Quantity of unit per package')),
                ('quota', models.IntegerField(default=0, help_text='The required minimum quantity when restocking has occurred')),
                ('storage', models.CharField(choices=[('A', 'Shed'), ('B', 'Shop')], max_length=2)),
                ('latest_qty', models.IntegerField(default=0, editable=False, help_text='The last quantity ordered')),
            ],
            options={
                'ordering': ['ordering'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Example: Dillanos', max_length=50)),
                ('email', models.EmailField(max_length=100)),
                ('send_email', models.BooleanField(default=True, help_text='Set "True" if you want orders to be sent to supplier email')),
                ('phone', models.CharField(help_text='Preferred format: 111-222-3333', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('order_number', models.IntegerField(default=1, help_text='The unique value used to identify an order')),
                ('order_qty', models.IntegerField(default=0, help_text='The amount of a given item to be ordered')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.item')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.supplier'),
        ),
        migrations.AddConstraint(
            model_name='item',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('package__length', 0), ('package_qty', 0)), models.Q(('package__length__gt', 0), ('package_qty__gt', 0)), _connector='OR'), name='packaging'),
        ),
    ]
