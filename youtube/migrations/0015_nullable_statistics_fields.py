# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-09 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0014_channelid_uniq__author_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='favorite_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='view_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
