# Generated by Django 4.1.7 on 2023-04-23 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_alter_team_half_duration_alter_team_team_formation_and_more'),
        ('lineups', '0003_lineup_number_subs_alter_lineup_opponent'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineup',
            name='first_goalie',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='lineup',
            name='second_goalie',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.CreateModel(
            name='SecondGoalie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.player')),
            ],
        ),
        migrations.CreateModel(
            name='FirstGoalie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.player')),
            ],
        ),
    ]