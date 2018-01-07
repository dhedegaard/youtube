# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('category', models.TextField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('author', models.TextField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('youtubeid', models.TextField(unique=True)),
                ('title', models.TextField(default=b'')),
                ('description', models.TextField(default=b'')),
                ('duration', models.IntegerField(default=0)),
                ('rating', models.DecimalField(
                    default=0.0, max_digits=10, decimal_places=8)),
                ('rating_count', models.IntegerField(default=0)),
                ('like_count', models.IntegerField(default=0)),
                ('view_count', models.IntegerField(default=0)),
                ('favorite_count', models.IntegerField(default=0)),
                ('comment_count', models.IntegerField(default=0)),
                ('uploaded', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(
                    related_name='videos', to='youtube.Category',
                    on_delete=models.CASCADE)),
                ('uploader', models.ForeignKey(
                    related_name='videos', to='youtube.Channel',
                    on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-uploaded'],
            },
            bases=(models.Model,),
        ),
    ]
