# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0004_channel_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('name', models.TextField(
                    unique=True, verbose_name='Tagname')),
                ('background_color', models.TextField(
                    default=b'#777', verbose_name='Background color')),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='tags',
            field=models.ManyToManyField(
                related_name='channels', to='youtube.Tag'),
        ),
    ]
