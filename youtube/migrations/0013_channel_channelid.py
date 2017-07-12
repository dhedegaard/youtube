# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from youtube.youtubeapi import fetch_channel_id_for_author


def fetch_channel_ids(apps, schema_editor):
    '''
    Fetches channel ids for all existing channels based on the author.
    '''
    Channel = apps.get_model('youtube', 'Channel')
    for channel in (Channel.objects.
                    filter(channelid__isnull=True).
                    select_for_update()):
        # Fetch channel ID for the channel in question.
        channelid = fetch_channel_id_for_author(channel.author)
        if not channelid:
            raise Exception(
                'Unable to find channelid for channel with author name: %s' %
                channel.author)
        # Assign it to the Channel object.
        channel.channelid = channelid
        channel.save()


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0012_remove_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='channelid',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(fetch_channel_ids),
    ]
