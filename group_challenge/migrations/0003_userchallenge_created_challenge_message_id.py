# Generated by Django 4.0.8 on 2022-10-16 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_challenge', '0002_userchallenge_is_random_opponent'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchallenge',
            name='created_challenge_message_id',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
