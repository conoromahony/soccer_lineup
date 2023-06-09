# Generated by Django 4.1.7 on 2023-04-24 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0006_player_preferred_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='preferred_position',
            field=models.CharField(choices=[('Goalie', 'Goalie'), ('Left_Back', 'Left Back'), ('Left_CB', 'Left Center Back'), ('Right_CB', 'Right Center Back'), ('Right_Back', 'Right Back'), ('Left_Mid', 'Left Mid'), ('Defensive_Mid', 'Defensive Mid'), ('Attaching_Mid', 'Attacking Mid'), ('Right_Mid', 'Right Mid'), ('Left_Striker', 'Left Striker'), ('Right_Striker', 'Right Striker')], max_length=13),
        ),
    ]
