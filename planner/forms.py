from django import forms
import re

class NameForm(forms.Form):
    your_name = forms.CharField(label = 'Your name', max_length=100)


CITY_CHOICES =  (
    ('Singapore', 'Singapore'),
    ('Australia', 'Australia'),
    ('Sydney', 'Sydney'),
    ('Melbourne', 'Melbourne'),
    ('Brisbane', 'Brisbane'),
    ('Perth', 'Perth'),
    ('Adelaide', 'Adelaide'),
    ('Gold Coast', 'Gold Coast'),
    ('Newcastle', 'Newcastle'),
    ('Canberra', 'Canberra'),
    ('New York City', 'New York City'),
)

class BasicForm(forms.Form):
    city = forms.ChoiceField(label = 'Country/ City', choices = CITY_CHOICES)
    num_days = forms.IntegerField(label = 'Number of days', initial = '5',
                                  widget=forms.TextInput(attrs={'placeholder': ''}))
    

class AdvancedForm(forms.Form):
    city = forms.ChoiceField(label = 'Country/ City', choices = CITY_CHOICES)
    start_date = forms.DateField(label = 'Tour start date',
                                widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    end_date = forms.DateField(label = 'Tour end date',
                              widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    start_time = forms.TimeField(label = 'Visit start time',
                                 widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}),
                                 initial = '10:00')
    end_time = forms.TimeField(label = 'Visit end time',
                               widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}),
                               initial = '20:00')
    lunch_time = forms.TimeField(label = 'Lunch time',
                                 widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}),
                                 initial = '12:00')
    lunch_duration = forms.IntegerField(label = 'Lunch duration',
                                        widget=forms.TextInput(attrs={'placeholder': 'In minutes'}),
                                        initial='60')
    dinner_time = forms.TimeField(label = 'Dinner time',
                                  widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}),
                                  initial='17:00')
    dinner_duration = forms.IntegerField(label = 'Dinner duration',
                                        widget=forms.TextInput(attrs={'placeholder': 'In minutes'}),
                                         initial='60')
    coordinates = forms.CharField(label = 'Visit Coordinates', required = False,
                                  help_text = "Planner will search for attractions with specified coordinates as the center. Can be left blank.",
                                  widget=forms.TextInput(attrs={'placeholder': 'latitude, longitude'}))
    

    
    def clean(self):
        cleaned_data = super(AdvancedForm, self).clean()
        
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        lunch_time = cleaned_data.get('lunch_time')
        lunch_duration = cleaned_data.get('lunch_duration')
        dinner_time = cleaned_data.get('dinner_time')
        dinner_duration = cleaned_data.get('dinner_duration')
        coordinates = cleaned_data.get('coordinates')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Invalid dates - start date cannot be after end date.")

        if start_time and end_time:
            if (start_time.hour*60 + start_time.minute + 4*60) > \
               (end_time.hour*60 + end_time.minute):
                raise forms.ValidationError("Invalid time - end time must be at least 4 hours after start time.")

        if lunch_time:
            if lunch_time < start_time:
                raise forms.ValidationError("Lunch time must be after start time.")

        if lunch_time and lunch_duration and dinner_time:
            if (lunch_time.hour*60 + lunch_time.minute + lunch_duration) >= \
               (dinner_time.hour*60 + dinner_time.minute):
                raise forms.ValidationError("Dinner time must be strictly after lunch ends.")

        if coordinates:
            pattern = '^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'
            if not bool(re.match(pattern, coordinates)):
                raise forms.ValidationError("Invalid coordinates.")




        
