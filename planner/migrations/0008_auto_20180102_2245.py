# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-02 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0007_auto_20171229_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='attraction',
            name='about',
            field=models.TextField(default='Information not available.', verbose_name='About'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attraction',
            name='categories',
            field=models.CharField(default='Others', max_length=200, verbose_name='Categories'),
            preserve_default=False,
        ),
    ]
