# Generated by Django 4.1.3 on 2023-03-14 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='default_message',
            field=models.CharField(default='', help_text="Example: Here's our order for today. Thank you!", max_length=250),
        ),
    ]
