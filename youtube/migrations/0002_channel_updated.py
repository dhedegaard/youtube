# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='updated',
            field=models.DateTimeField(
                default=timezone.make_aware(
                    datetime.datetime(2015, 2, 27, 21, 13, 37, 642777),
                    timezone.get_current_timezone()),
                auto_now_add=True),
            preserve_default=False,
        ),
    ]
