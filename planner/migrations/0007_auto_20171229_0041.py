# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-28 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0006_auto_20171226_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attraction',
            options={'ordering': ['country', '-score']},
        ),
        migrations.AlterField(
            model_name='attraction',
            name='address',
            field=models.CharField(max_length=200, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='coordinates',
            field=models.CharField(max_length=50, verbose_name='Coordinates'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='country',
            field=models.CharField(max_length=50, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_0',
            field=models.CharField(max_length=50, verbose_name='0'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_1',
            field=models.CharField(max_length=50, verbose_name='1'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_2',
            field=models.CharField(max_length=50, verbose_name='2'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_3',
            field=models.CharField(max_length=50, verbose_name='3'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_4',
            field=models.CharField(max_length=50, verbose_name='4'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_5',
            field=models.CharField(max_length=50, verbose_name='5'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='day_6',
            field=models.CharField(max_length=50, verbose_name='6'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='duration',
            field=models.IntegerField(verbose_name='Durations'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Attraction'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='num_reviews',
            field=models.IntegerField(verbose_name='NumReviews'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=2, verbose_name='Rating'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='review_summary',
            field=models.TextField(verbose_name='ReviewsSummary'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='score',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Score'),
        ),
    ]
