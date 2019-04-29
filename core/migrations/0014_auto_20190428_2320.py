# Generated by Django 2.0.5 on 2019-04-28 23:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_userlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='problempost',
            name='origin_link',
            field=models.CharField(blank=True, default='', help_text='留空的话视作原创', max_length=255, verbose_name='原文链接'),
        ),
        migrations.AddField(
            model_name='problempost',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='core.OnlineJudgeProblem', verbose_name='对应题目'),
        ),
        migrations.AddField(
            model_name='problempost',
            name='rating_difficulty',
            field=models.IntegerField(default=0, help_text='1-5，最难为5，最容易为1，0的话是尚未评分', verbose_name='难度评级'),
        ),
        migrations.AlterField(
            model_name='problempost',
            name='problems',
            field=models.ManyToManyField(related_name='posts_related', to='core.OnlineJudgeProblem', verbose_name='关联题目'),
        ),
    ]
