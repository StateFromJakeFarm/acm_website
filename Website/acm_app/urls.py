from django.urls import path
from django.contrib.auth import views as adminviews

from . import views

# Create your views here.

urlpatterns = [
    path('accounts/register/', views.register, name='register'),           # Create new account
    path('accounts/login/', adminviews.LoginView.as_view(), name='login'), # Login to existing account
    path('accounts/logout/', views.logout_view, name='logout'),            # Logout of account
    path('', views.home, name='home'),                                     # Landing page
    path('problems', views.problems, name='problems'),                     # Browse and solve problems
    path('edit/', views.create_or_edit_problem, name='edit'),              # Create and edit problems
    path('leaderboard', views.leaderboard, name='leaderboards'),           # School-wide leaderboard
]
