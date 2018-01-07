from __future__ import unicode_literals
import re

from django import forms
from django.utils.html import format_html

from .youtubeapi import fetch_channel_id_for_author, check_channel_id_exists
from .models import Channel


class AddChannelForm(forms.Form):
    channel = forms.CharField(label='Add a channel')

    def clean_channel(self):
        channel = self.cleaned_data['channel']

        # If the channel is an URL, convert the URL to the channel name
        # expected by the system.
        rc = re.findall(
            r'^https:\/\/www.youtube.com\/(?:user|channel)\/([^\/]+)\/?.*?$',
            channel, re.I | re.U)
        if rc:
            channel = rc[0]

        # Check to see if the channel is an author.
        channelid = fetch_channel_id_for_author(channel)

        # Check to see if the channel already exists.
        if channelid:
            existing_channel = (
                Channel.objects
                .filter(channelid=channelid)
                .first())
        else:
            existing_channel = Channel.objects.filter(author=channel).first()

        if existing_channel:
            raise forms.ValidationError(format_html(
                'Channel already exists in the system under the title: '
                '<b>{0}</b>',
                existing_channel.title))

        # Check to see if the channel already is a channel id.
        if not channelid and check_channel_id_exists(channel):
            channelid = channel
        # Otherwise notify the user of unknown input.
        if not channelid:
            raise forms.ValidationError(format_html(
                'Channel does not seem to exist: <b>{0}</b>',
                channel))
        self.cleaned_data['channelid'] = channelid

        return channel
