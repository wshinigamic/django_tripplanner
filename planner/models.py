# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.urls import reverse

class Attraction(models.Model):

    name = models.CharField('Attraction', max_length = 200)
    rating = models.DecimalField('Rating', max_digits = 2, decimal_places = 1)
    num_reviews = models.IntegerField('NumReviews')
    address = models.CharField('Address', max_length = 200)
    duration = models.IntegerField('Durations')
    score = models.DecimalField('Score', max_digits = 10, decimal_places = 2)
    coordinates = models.CharField('Coordinates', max_length = 50)
    review_summary = models.TextField('ReviewsSummary')
    day_0 = models.CharField('0', max_length = 50)
    day_1 = models.CharField('1', max_length = 50)
    day_2 = models.CharField('2', max_length = 50)
    day_3 = models.CharField('3', max_length = 50)
    day_4 = models.CharField('4', max_length = 50)
    day_5 = models.CharField('5', max_length = 50)
    day_6 = models.CharField('6', max_length = 50)
    country = models.CharField('Country', max_length = 50)

    class Meta:
        ordering = ['country', '-score']
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('attraction-detail', args = [str(self.id)])
    

class Country(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name
