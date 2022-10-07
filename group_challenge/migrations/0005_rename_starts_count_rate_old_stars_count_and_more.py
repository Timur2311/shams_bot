# Generated by Django 4.0.7 on 2022-09-16 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_challenge', '0004_remove_privatechallenge_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rate',
            old_name='starts_count',
            new_name='old_stars_count',
        ),
        migrations.RemoveField(
            model_name='rate',
            name='private_challenge',
        ),
        migrations.AddField(
            model_name='rate',
            name='stars_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='progress',
            name='challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenge_progress', to='group_challenge.userchallenge'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='user_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_progresses', to='group_challenge.usertask'),
        ),
        migrations.DeleteModel(
            name='PrivateChallenge',
        ),
    ]
