"""Choose player positions
"""
from django import forms
from .models import Player, Team

class ChoosePositionsForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('is_goalie', 'preferred_position', 'is_left_full', 'is_right_full', 'is_center_back', 'is_sweeper',
                  'is_stopper', 'is_left_mid', 'is_right_mid', 'is_attacking_mid', 'is_left_striker',
                  'is_right_striker')

class NewPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name', 'preferred_position', 'is_goalie', 'is_left_full', 'is_right_full', 'is_center_back',
                  'is_sweeper', 'is_stopper', 'is_left_mid', 'is_right_mid', 'is_attacking_mid', 'is_left_striker',
                  'is_right_striker')

class NewTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('team_size', 'team_formation', 'half_duration')
        widgets = {
            'team_size': forms.Select(
                choices=Team.TeamSize,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
            'team_formation': forms.Select(
                choices=Team.TeamFormation,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
            'half_duration': forms.Select(
                choices=Team.HalfDuration,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
        }