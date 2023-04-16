# Generated by Django 4.1.7 on 2023-04-15 21:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lineup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(max_length=20)),
                ('team_name', models.CharField(max_length=20)),
                ('team_size', models.CharField(choices=[('11', '11 vs. 11')], default='11', max_length=2)),
                ('team_formation', models.CharField(choices=[('442d', '4-4-2 (diamond)')], default='442d', max_length=4)),
                ('half_duration', models.CharField(choices=[('35', '35 minutes')], default='35', max_length=2)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
