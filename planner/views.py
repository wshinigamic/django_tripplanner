# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from .models import Attraction
from .forms import NameForm
from .forms import BasicForm
from .forms import AdvancedForm

def attractions_data(request):
    num_attractions = Attraction.objects.all().count()

    return render(
        request,
        'attractions_data.html',
        context = {'num_attractions': num_attractions}
    )


from django_pandas.io import read_frame
import planner

CITY_COORD = {
    'Singapore': (1.284491, 103.847282),
    'Australia': (-33.884244, 151.194860),
    'Sydney': (-33.884244, 151.194860),
    'Melbourne': (-37.813453, 144.964051),
    'Perth': (-31.950509, 115.860469),
    'Adelaide': (-34.928501, 138.600744),
    'Gold Coast': (-28.016659, 153.399985),
    'Newcastle': (-32.928334, 151.781666),
    'Canberra': (-35.280937, 149.130009),
    'New York City': (40.7586153, -73.9783659),
    }

ACTIVITIES_INDEX = {
    'a': 'Nature & Parks',
    'b': 'Sights & Landmarks',
    'c': 'Shopping',
    'd': 'Outdoor Activities',
    'e': 'Museums',
    'f': 'Features Animals',
    'g': 'Fun & Games',
    'h': 'Points of Interest & Landmarks'
    }
    

def index(request):

    if request.method == 'POST':
        form = BasicForm(request.POST)
        if form.is_valid():
            num_days = form.cleaned_data['num_days']
            city = form.cleaned_data['city']
            coord = CITY_COORD[city]
            if city == 'Singapore':
                country = 'Singapore'
            elif city == 'New York City':
                country = 'USA'
            else:
                country = 'Australia'
            
            qs = Attraction.objects.filter(country__iexact=country)
            df = read_frame(qs)
            columns={
                'name' : 'Attraction',
                'rating': 'Rating',
                'num_reviews': 'NumReviews',
                'address': 'Address',
                'duration': 'Durations',
                'score': 'Score',
                'coordinates': 'Coordinates',
                'review_summary': 'ReviewsSummary',
                'day_0': '0',
                'day_1': '1',
                'day_2': '2',
                'day_3': '3',
                'day_4': '4',
                'day_5': '5',
                'day_6': '6',
                'about': 'About',
                'categories': 'Categories',
                }
            df = df.rename(columns = columns)
            df = df.sort_values(by = 'Score', ascending = False)
            df = df[~df.Categories.str.contains('Food')]
            df = df.reset_index(drop = True)
            start_coords = [coord]*num_days
            end_coords = [coord]*num_days
            
            #output = planner.main_binary_search(df, num_days,
            #                      visit_coord = (1.284491, 103.847282))
            output = planner.main_binary_search(df, num_days,
                                                start_coords = start_coords,
                                                end_coords = end_coords)
            if output is not None:
                planned_address = output[2]
                planned_reviews_summary = output[3]
                planned_about = output[10]
                events_list, time_schedules = planner.get_schedule(output)
                str_schedule = planner.readable_list(events_list, time_schedules,
                                                     planned_address,
                                                     planned_reviews_summary,
                                                     planned_about)
            else:
                str_schedule = None
            return render(
                request,
                'output.html',
                context = {'schedule': str_schedule}
            )

    else:
        form = BasicForm()
    
    return render(
        request,
        'basic_form.html',
        context = {'form': form}
    )

import datetime

def advanced_form(request):

    if request.method == 'POST':
        form = AdvancedForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            lunch_time = form.cleaned_data['lunch_time']
            lunch_duration = form.cleaned_data['lunch_duration']
            dinner_time = form.cleaned_data['dinner_time']
            dinner_duration = form.cleaned_data['dinner_duration']
            coordinates = form.cleaned_data['coordinates']

            num_days = (end_date - start_date).days + 1
            start_day = (start_date.weekday() + 1) % 7
            start_time = start_time.hour*60 + start_time.minute
            end_time = end_time.hour*60 + end_time.minute
            lunch_time = lunch_time.hour*60 + lunch_time.minute
            dinner_time = dinner_time.hour*60 + dinner_time.minute

            coord = CITY_COORD[city]
            if city == 'Singapore':
                country = 'Singapore'
            elif city == 'New York City':
                country = 'USA'
            else:
                country = 'Australia'
                
            if len(coordinates) == 0:
                start_coords = [coord] * num_days
                end_coords = [coord] * num_days
            else:
                start_coords = [eval(coordinates)] * num_days
                end_coords = [eval(coordinates)] * num_days
                
            qs = Attraction.objects.filter(country__iexact=country)
            df = read_frame(qs)
            columns={
                'name' : 'Attraction',
                'rating': 'Rating',
                'num_reviews': 'NumReviews',
                'address': 'Address',
                'duration': 'Durations',
                'score': 'Score',
                'coordinates': 'Coordinates',
                'review_summary': 'ReviewsSummary',
                'day_0': '0',
                'day_1': '1',
                'day_2': '2',
                'day_3': '3',
                'day_4': '4',
                'day_5': '5',
                'day_6': '6',
                'about': 'About',
                'categories': 'Categories',
                }
            df = df.rename(columns = columns)
            df = df.sort_values(by = 'Score', ascending = False)
            df = df[~df.Categories.str.contains('Food')]
            df = df.reset_index(drop = True)

            """list_1 = []
            list_0 = []
            for index in ACTIVITIES_INDEX:
                if form.cleaned_data['index'] == 1:
                    list_1.append(ACTIVITIES_INDEX[index])
                elif form.cleaned_data['index'] == 0:
                    list_0.append(ACTIVITIES_INDEX[index])
            for category in list_1:
                mask = df.Categories.str.contains(category)
                column_name = 'Score'
                df.loc[mask, column_name] *= 1.5
            for category in list_0:
                mask = df.Categories.str.contains(category)
                column_name = 'Score'
                df.loc[mask, column_name] *= 2.0/3"""            
            
            output = planner.main_binary_search(
                df, num_days, start_coords = start_coords,
                end_coords = end_coords, start_day = start_day,
                start_time = start_time, end_time = end_time,
                lunch_time = lunch_time, lunch_duration = lunch_duration,
                dinner_time = dinner_time, dinner_duration = dinner_duration
            )
            
            if output is not None:
                planned_address = output[2]
                planned_reviews_summary = output[3]                
                planned_about = output[10]
                events_list, time_schedules = planner.get_schedule(output)
                str_schedule = planner.readable_list(events_list, time_schedules,
                                                     planned_address,
                                                     planned_reviews_summary,
                                                     planned_about)
            else:
                str_schedule = None
            return render(
                request,
                'output.html',
                context = {'schedule': str_schedule}
            )

    else:
        form = AdvancedForm()
    
    return render(
        request,
        'advanced_form.html',
        context = {'form': form}
    )
