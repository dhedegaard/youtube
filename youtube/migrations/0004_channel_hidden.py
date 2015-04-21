# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0003_auto_20150403_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
