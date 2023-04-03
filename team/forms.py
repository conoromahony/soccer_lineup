"""Choose player positions
"""
from django import forms
from .models import Player

class ChoosePositionsForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('is_goalie', 'is_left_full', 'is_right_full', 'is_center_back', 'is_sweeper', 'is_stopper',
                  'is_left_mid', 'is_right_mid', 'is_attacking_mid', 'is_left_striker', 'is_right_striker')
