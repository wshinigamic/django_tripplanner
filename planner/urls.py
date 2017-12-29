from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^index1/$', views.index1, name = 'index1'),
    url(r'^advanced_form/$', views.advanced_form, name = 'advanced_form'),
]
