# Generated by Django 2.0.5 on 2019-04-27 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_problempost_excerpt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemcategory',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='分类名称'),
        ),
    ]