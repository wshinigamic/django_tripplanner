from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label = 'Your name', max_length=100)


class BasicForm(forms.Form):
    num_days = forms.IntegerField(label = 'Number of days')
    country = forms.CharField(label = 'Country', max_length = 50)

class AdvancedForm(forms.Form):
    num_days = forms.IntegerField(label = 'Number of days')
    start_day = forms.TimeField(label = 'Tour start date')
    end_day = forms.TimeField(label = 'Tour end date')
    start_time = forms.TimeField(label = 'Day start time')
    end_time = forms.TimeField(label = 'Day end time')
    lunch_time = forms.TimeField(label = 'Lunch time')
    lunch_duration = forms.IntegerField(label = 'Lunch duration',
                                        help_text="In minutes")
    dinner_time = forms.TimeField(label = 'Dinner time')
    dinner_duration = forms.IntegerField(label = 'Lunch duration',
                                        help_text="In minutes")
    
    
