from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


# Create your models here.
class Player(models.Model):
    class PreferredPosition(models.TextChoices):
        GOALIE = "goalie", _("Goalie")
        LEFT_BACK = "left_full", _("Left Back")
        LEFT_CB = "center_back", _("Left Center Back")
        RIGHT_CB = "sweeper", _("Right Center Back")
        RIGHT_BACK = "right_full", _("Right Back")
        LEFT_MID = "left_mid", _("Left Mid")
        DEFENSIVE_MID = "stopper", _("Defensive Mid")
        ATTACKING_MID = "attacking_mid", _("Attacking Mid")
        RIGHT_MID = "right_mid", _("Right Mid")
        LEFT_STRIKER = "left_striker", _("Left Striker")
        RIGHT_STRIKER = "right_striker", _("Right Striker")

    name = models.CharField(max_length=20)
    team_name = models.CharField(max_length=20)
    preferred_position = models.CharField(
        max_length=13,
        choices=PreferredPosition.choices
    )
    is_goalie = models.BooleanField()
    is_left_full = models.BooleanField()
    is_right_full = models.BooleanField()
    is_center_back = models.BooleanField()
    is_sweeper = models.BooleanField()
    is_stopper = models.BooleanField()
    is_left_mid = models.BooleanField()
    is_right_mid = models.BooleanField()
    is_attacking_mid = models.BooleanField()
    is_left_striker = models.BooleanField()
    is_right_striker = models.BooleanField()
    objects = models.Manager()      # The default manager

    def __str__(self):
        # Returns a string representation of the model.
        return self.name

    def get_absolute_url(self):
        return reverse('team:player_detail', args=[self.name])


class Team(models.Model):
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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        # Returns a string representation of the model.
        return self.team_name
