# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-19 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0019_savedsearch_modified_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]