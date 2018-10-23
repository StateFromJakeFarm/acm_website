from django.urls import path

from . import views

# Create your views here.

urlpatterns = [
    path('', views.login, name='login'),
    path('index', views.index, name='index'),
]