# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 01:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0004_supersearch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supersearch',
            name='searches',
        ),
        migrations.AddField(
            model_name='search',
            name='super_search',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='amazon.SuperSearch'),
        ),
    ]