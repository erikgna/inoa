# Generated by Django 4.2 on 2023-04-22 19:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_remove_stock_last_reload_remove_stock_output_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdata',
            name='close_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='high_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='low_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='open_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='volume',
            field=models.IntegerField(default=0),
        ),
    ]
