# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0008_video_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='like_count',
        ),
        migrations.RemoveField(
            model_name='video',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='video',
            name='rating_count',
        ),
    ]
