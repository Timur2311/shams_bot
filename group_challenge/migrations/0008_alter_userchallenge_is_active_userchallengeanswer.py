# Generated by Django 4.0.8 on 2022-10-11 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0010_rename_user_answer_userexamanswer_user_exam'),
        ('tgbot', '0004_user_name'),
        ('group_challenge', '0007_remove_task_user_remove_task_user_challenge_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userchallenge',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='UserChallengeAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_ids', models.CharField(max_length=255, null=True)),
                ('answered', models.BooleanField(default=False)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.user')),
                ('user_challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer', to='group_challenge.userchallenge')),
            ],
        ),
    ]
