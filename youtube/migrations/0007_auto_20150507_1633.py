# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0006_channel_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='uploads_playlist',
            field=models.TextField(default=b''),
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
