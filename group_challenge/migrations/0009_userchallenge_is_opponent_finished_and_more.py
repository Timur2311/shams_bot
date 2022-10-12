# Generated by Django 4.0.8 on 2022-10-11 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_challenge', '0008_alter_userchallenge_is_active_userchallengeanswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchallenge',
            name='is_opponent_finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userchallenge',
            name='is_user_finished',
            field=models.BooleanField(default=False),
        ),
    ]
