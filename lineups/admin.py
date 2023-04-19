from django.contrib import admin
from .models import Lineup


# Register your models here.
@admin.register(Lineup)
class LineupAdmin(admin.ModelAdmin):
    list_display = ('game_id', 'opponent', 'game_date', 'team_name', 'team_size', 'team_formation', 'half_duration',
                    'owner')
