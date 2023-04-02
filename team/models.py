from django.db import models
from django.urls import reverse

# Create your models here.
class AllPlayers(models.Manager):
    def get_queryset(self):
        return super(AllPlayers, self).get_queryset()

class Player(models.Model):
    name = models.CharField(max_length=20)
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
    all_players = AllPlayers()      # Custom Manager to return all players

    def __str__(self):
        # Returns a string representation of the model.
        return self.name

    def get_absolute_url(self):
        return reverse('team:player_detail', args=[self.name])

