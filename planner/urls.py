from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^advanced_form/$', views.advanced_form, name = 'advanced_form'),    
    url(r'^attractions_data/$', views.attractions_data, name = 'attractions_data'),
]
