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
    path('edit', views.create_or_edit_problem, name='create'),            # Create new problem
    path('edit/<slug:slug>', views.create_or_edit_problem, name='edit'),   # Edit existing problem
    path('leaderboard', views.leaderboard, name='leaderboards'),           # School-wide leaderboard
    path('contests', views.all_contests, name='all contests'),             # TODO: show all contests
    path('contests/create', views.create_or_edit_problem, name='create contest'), # Create new contest
    path('contests/<slug:slug>/edit', views.create_or_edit_problem, name='edit contest'), # Edit existing contest
    url(r'^markdownx/', include(markdownx)),
    path('chat/', views.chat, name='chat'),
    re_path(r'^chat/(?P<room_name>[^/]+)/$', views.room, name='room'),
    re_path(r'^chat_headless/(?P<room_name>[^/]+)/$', views.room_headless, name='room_headless'),
]
