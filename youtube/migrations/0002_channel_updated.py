# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='updated',
            field=models.DateTimeField(
                default=datetime.datetime(2015, 2, 27, 21, 13, 37, 642777),
                auto_now_add=True),
            preserve_default=False,
        ),
    ]
