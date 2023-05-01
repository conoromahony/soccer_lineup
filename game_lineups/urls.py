# game_lineups URL Configuration
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls', namespace='home')),
    path('team/', include('team.urls', namespace='team')),
    path('users/', include('users.urls', namespace='users')),
    path('lineups/', include('lineups.urls', namespace='lineups')),
]