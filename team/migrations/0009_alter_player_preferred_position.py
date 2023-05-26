# Generated by Django 4.1.7 on 2023-05-25 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0008_alter_player_preferred_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='preferred_position',
            field=models.CharField(choices=[('goalie', 'Goalie'), ('left_full', 'Left Back'), ('center_back', 'Left Center Back'), ('sweeper', 'Right Center Back'), ('right_full', 'Right Back'), ('left_mid', 'Left Mid'), ('stopper', 'Defensive Mid'), ('attacking_mid', 'Attacking Mid'), ('right_mid', 'Right Mid'), ('left_striker', 'Left Striker'), ('right_striker', 'Right Striker')], max_length=13),
        ),
    ]