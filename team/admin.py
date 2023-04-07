from django.contrib import admin

# Register your models here.
from django.contrib import admin
# The "dot" before "models" tells Django to look for models.py in the same directory as this file.
from .models import Player, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'team_size', 'team_formation', 'half_duration')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_name', 'is_goalie', 'is_left_full', 'is_right_full', 'is_sweeper', 'is_center_back', 'is_stopper', 'is_left_mid', 'is_right_mid', 'is_attacking_mid', 'is_left_striker', 'is_right_striker')
    list_filter = ('name', 'is_goalie', 'is_left_full', 'is_right_full', 'is_sweeper', 'is_center_back', 'is_stopper', 'is_left_mid', 'is_right_mid', 'is_attacking_mid', 'is_left_striker', 'is_right_striker')
