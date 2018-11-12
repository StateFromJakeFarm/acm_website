from django.urls import path

from . import views

# Create your views here.

urlpatterns = [
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login, name='login'),
    path('', views.home, name='home'),
]