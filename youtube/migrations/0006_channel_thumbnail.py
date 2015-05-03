# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0005_auto_20150501_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='thumbnail',
            field=models.TextField(default=b''),
        ),
    ]
