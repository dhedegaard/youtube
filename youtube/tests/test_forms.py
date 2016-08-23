from __future__ import unicode_literals

import mock
from django.test import TestCase

from ..models import Channel
from ..forms import AddChannelForm


class AddChanelFormTest(TestCase):
    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__fetch_from_url(self, does_channel_author_exist_patch):
        does_channel_author_exist_patch.return_value = True

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/user/testuser/videos',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(does_channel_author_exist_patch.called)

    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__fetch_from_url_no_slash(self, does_channel_author_exist_patch):
        does_channel_author_exist_patch.return_value = True

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/user/testuser',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(does_channel_author_exist_patch.called)

    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__fetch_from_url_no_slash(self, does_channel_author_exist_patch):
        does_channel_author_exist_patch.return_value = True

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/channel/testuser/videos',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(does_channel_author_exist_patch.called)
    def test__fetch_existing_channel(self):
        Channel.objects.create(
            author='testchannel',
            title='Test Channel',
        )

        form = AddChannelForm({
            'channel': 'testchannel',
        })

        self.assertFalse(form.is_valid())
        self.assertTrue('channel' in form.errors)
        self.assertEqual(form.errors['channel'][0],
                         'Channel already exists in the system '
                         'under the title: <b>Test Channel</b>')

    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__channel_does_not_exist(self, does_channel_author_exist_patch):
        does_channel_author_exist_patch.return_value = False

        form = AddChannelForm({
            'channel': 'testchannel',
        })

        self.assertFalse(form.is_valid())
        self.assertTrue('channel' in form.errors)
        self.assertEqual(form.errors['channel'][0],
                         'Channel does not seem to exist: <b>testchannel</b>')
        self.assertTrue(does_channel_author_exist_patch.called)
