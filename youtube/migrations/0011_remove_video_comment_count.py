# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0010_missing_indices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='comment_count',
        ),
    ]
