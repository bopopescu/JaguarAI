# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0016_auto_20170419_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='search',
            options={'ordering': ('-avg_revenue',), 'verbose_name_plural': 'Searches'},
        ),
        migrations.AddField(
            model_name='search',
            name='avg_review_count',
            field=models.FloatField(default=0),
        ),
    ]