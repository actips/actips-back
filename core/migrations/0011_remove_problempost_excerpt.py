# Generated by Django 2.0.5 on 2019-04-26 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20190426_1340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problempost',
            name='excerpt',
        ),
    ]
