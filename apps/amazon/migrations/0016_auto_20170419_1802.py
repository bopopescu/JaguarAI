# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0015_auto_20170418_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='avg_price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='search',
            name='avg_volume',
            field=models.FloatField(default=0),
        ),
    ]
