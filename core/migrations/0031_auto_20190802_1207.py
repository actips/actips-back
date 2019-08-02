# Generated by Django 2.2.1 on 2019-08-02 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20190801_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinejudgeproblem',
            name='attachments',
            field=models.TextField(default='[]', help_text='JSON分割的附件链接清单，采集时应预处理进 /media/oj/???/attachments/checksum，记录原文件名 [{filename: "...", checksum: "..."}, ...]', verbose_name='附件清单'),
        ),
        migrations.AddField(
            model_name='onlinejudgeproblem',
            name='is_pdf',
            field=models.BooleanField(default=False, verbose_name='是否pdf内容'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comments_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='onlinejudgesubmission',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='onlinejudgesubmissions_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='problempost',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='problemposts_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userlog',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='userlogs_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
            preserve_default=False,
        ),
    ]