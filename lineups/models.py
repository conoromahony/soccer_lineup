from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from team.models import Player


# Create your models here.
class Lineup(models.Model):
    class TeamSize(models.TextChoices):
        # SEVEN = "7", _("7 vs. 7")
        # NINE = "9", _("9 vs. 9")
        ELEVEN = "11", _("11 vs. 11")

    class TeamFormation(models.TextChoices):
        FOUR_FOUR_TWO_D = "442d", _("4-4-2 (diamond)")
        # FOUR_FOUR_TWO_F = "442f", _("4-4-2 (flat)")
        # FOUR_THREE_THREE = "433", _("4-3-3")

    class HalfDuration(models.TextChoices):
        # THIRTY = "30", _("30 minutes")
        THIRTY_FIVE = "35", _("35 minutes")
        # FORTY = "40", _("40 minutes")
        # FORTY_FIVE = "45", _("45 minutes")

    class FirstGoalie(models.Model):
        name = models.ForeignKey(Player, on_delete=models.CASCADE)

    class SecondGoalie(models.Model):
        name = models.ForeignKey(Player, on_delete=models.CASCADE)

    game_id = models.CharField(max_length=20)
    opponent = models.CharField(max_length=40, default='')
    game_date = models.DateField()
    team_name = models.CharField(max_length=20)
    team_size = models.CharField(
        max_length=2,
        choices=TeamSize.choices,
        default=TeamSize.ELEVEN,
    )
    team_formation = models.CharField(
        max_length=4,
        choices=TeamFormation.choices,
        default=TeamFormation.FOUR_FOUR_TWO_D,
    )
    half_duration = models.CharField(
        max_length=2,
        choices=HalfDuration.choices,
        default=HalfDuration.THIRTY_FIVE,
    )
    first_goalie = models.CharField(
        max_length=20,
        default=''
    )
    second_goalie = models.CharField(
        max_length=20,
        default=''
    )
    number_subs = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        # Returns a string representation of the model.
        return self.game_id
