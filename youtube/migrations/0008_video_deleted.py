# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0007_auto_20150507_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='deleted',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
