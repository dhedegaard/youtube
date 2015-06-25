from __future__ import unicode_literals
import re

from django import forms
from django.utils.html import format_html

from .utils import does_channel_author_exist
from .models import Channel


class AddChannelForm(forms.Form):
    channel = forms.CharField(label=u'Add a channel')

    def clean_channel(self):
        channel = self.cleaned_data['channel']

        # If the channel is an URL, convert the URL to the channel name
        # expected by the system.
        rc = re.findall(r'^https:\/\/www.youtube.com\/user\/([^\/]+)\/?.*?$',
                        channel, re.I | re.U)
        if rc:
            channel = rc[0]

        # Check to see if the channel already exists.
        existing_channel = Channel.objects.filter(author=channel).first()
        if existing_channel:
            raise forms.ValidationError(format_html(
                'Channel already exists in the system under the title: '
                '<b>{0}</b>',
                existing_channel.title))

        # Check to see if the channel is valid in the API.
        if not does_channel_author_exist(channel):
            raise forms.ValidationError(format_html(
                'Channel does not seem to exist: <b>{0}</b>',
                channel))

        return channel
