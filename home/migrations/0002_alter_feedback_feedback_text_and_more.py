# Generated by Django 4.1.7 on 2023-04-19 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='feedback_text',
            field=models.TextField(verbose_name='And your feedback:'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='from_email',
            field=models.EmailField(max_length=254, verbose_name='Your email address:'),
        ),
    ]
