# Generated by Django 4.1.2 on 2022-10-26 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='email',
            field=models.EmailField(default='person@example.com', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='phone',
            field=models.CharField(default='111-222-3333', help_text='Preferred format: 111-222-3333', max_length=20),
            preserve_default=False,
        ),
    ]
