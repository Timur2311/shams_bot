# Generated by Django 4.0.8 on 2022-10-07 02:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_rm_unused_fields'),
        ('exam', '0007_exam_stage_exam_tour'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=2048)),
                ('stage', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=16)),
                ('tour', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], max_length=16)),
                ('time', models.IntegerField(default=10, verbose_name="Savolar uchun mo'ljallangan vaqt(sekund)")),
                ('true_definition', models.TextField(max_length=65536)),
                ('true_answered_users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.user')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=256)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='exam.question')),
            ],
        ),
        migrations.AlterField(
            model_name='exam',
            name='questions',
            field=models.ManyToManyField(to='exam.question'),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='questions',
            field=models.ManyToManyField(to='exam.question'),
        ),
        migrations.AlterField(
            model_name='userexamanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.question'),
        ),
    ]
