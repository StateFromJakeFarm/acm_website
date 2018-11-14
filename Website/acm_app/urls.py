from django.urls import path
from django.contrib.auth import views as adminviews

from . import views

# Create your views here.

urlpatterns = [
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', adminviews.LoginView.as_view(), name='login'),
    path('', views.home, name='home'),
    path('problems', views.problems, name='problems'),
    path('leaderboard', views.leaderboard, name='leaderboards'),
]
