# Generated by Django 4.1.7 on 2023-05-01 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lineups', '0005_lineup_positions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lineup',
            old_name='number_subs',
            new_name='num_players',
        ),
    ]
