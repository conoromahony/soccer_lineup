from django import forms
from .models import Lineup


class NewLineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ('opponent', 'game_date')

