# Generated by Django 2.0.5 on 2019-04-27 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0012_auto_20190427_1352'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
                ('action', models.CharField(max_length=20, verbose_name='动作')),
                ('remark', models.CharField(blank=True, default='', max_length=45, verbose_name='备注')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userlogs_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
            ],
            options={
                'verbose_name': '用户日志',
                'verbose_name_plural': '用户日志',
                'db_table': 'core_user_log',
            },
        ),
    ]
