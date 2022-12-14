# Generated by Django 4.0.8 on 2022-10-17 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_user_region'),
        ('group_challenge', '0005_userchallenge_opponent_chat_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userchallenge',
            name='opponent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='as_opponent', to='tgbot.user'),
        ),
        migrations.AlterField(
            model_name='userchallenge',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='as_owner', to='tgbot.user'),
        ),
    ]
