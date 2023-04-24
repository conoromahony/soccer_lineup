from django import forms
from .models import Lineup
from team.models import Team, Player


class DateInput(forms.DateInput):
    input_type = 'date'


class NewLineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ('opponent', 'game_date', 'team_formation', 'first_goalie', 'second_goalie')
        widgets = {
            'opponent': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'game_date': DateInput(
                attrs={'class': 'form-control'}
            ),
            'team_formation': forms.Select(
                choices=Team.TeamFormation,
                attrs={'class': 'form-select', 'style': 'max-width: 300px;'}
            ),
        }

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        super(NewLineupForm, self).__init__(*args, **kwargs)
        self.fields['first_goalie'] = forms.ChoiceField(
            label="First Half Goalie",
            choices=choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'}))
        self.fields['second_goalie'] = forms.ChoiceField(
            label="Second Half Goalie",
            choices=choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'}))
