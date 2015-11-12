# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0009_auto_20151013_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='hidden',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='title',
            field=models.TextField(default='', db_index=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='uploaded',
            field=models.DateTimeField(db_index=True),
        ),
    ]
