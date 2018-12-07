from django.urls import path, re_path
from django.conf.urls import url, include
from django.contrib.auth import views as adminviews
from markdownx import urls as markdownx

from . import views

# Create your views here.

urlpatterns = [
    path('', views.home, name='home'),                                     # Landing page
    path('accounts/register/', views.register, name='register'),           # Create new account
    path('accounts/login/', adminviews.LoginView.as_view(), name='login'), # Login to existing account
    path('accounts/logout/', views.logout_view, name='logout'),            # Logout of account
    path('problems', views.all_problems, name='all problems'),             # Browse and solve problems
    path('problems/<slug:slug>', views.problem, name='single problem'),    # Submission page for single problem
    path('edit/', views.create_or_edit_problem, name='edit'),              # Create and edit problems
    path('leaderboard', views.leaderboard, name='leaderboards'),           # School-wide leaderboard
    url(r'^markdownx/', include(markdownx)),
    path('chat/', views.chat, name='chat'),
    re_path(r'^chat/(?P<room_name>[^/]+)/$', views.room, name='room'),
]
