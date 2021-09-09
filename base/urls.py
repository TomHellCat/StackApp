from django.urls import path
from django.conf.urls import url, include 


from . import views

app_name = 'base'

urlpatterns = [
    path('',views.home, name='home'),
    path('result/<str:pk1>/<str:pk2>',views.result, name='result'),
]