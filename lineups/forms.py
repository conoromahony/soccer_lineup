from django import forms
from .models import Lineup


class NewLineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ('game_id', 'team_name', 'team_size', 'team_formation', 'half_duration')
        widgets = {
            'team_size': forms.Select(
                choices=Lineup.TeamSize,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
            'team_formation': forms.Select(
                choices=Lineup.TeamFormation,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
            'half_duration': forms.Select(
                choices=Lineup.HalfDuration,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
        }
