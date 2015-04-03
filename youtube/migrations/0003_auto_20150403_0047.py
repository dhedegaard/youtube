# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0002_channel_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='title',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='video',
            name='updated',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
