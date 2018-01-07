from __future__ import unicode_literals

import mock
from django.test import TestCase

from ..models import Channel
from ..forms import AddChannelForm


class AddChannelFormTest(TestCase):
    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__fetch_from_url(self, fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = 1234

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/user/testuser/videos',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(fetch_channel_id_for_author_patch.called)

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__fetch_from_url_no_slash(
            self, fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = 1234

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/user/testuser',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(fetch_channel_id_for_author_patch.called)

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__fetch_from_url_no_slash__with_channel(
            self, fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = 1234

        form = AddChannelForm({
            'channel': 'https://www.youtube.com/channel/testuser/videos',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channel'], 'testuser')
        self.assertTrue(fetch_channel_id_for_author_patch.called)

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__fetch_existing_channel(
            self, fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = None
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
        fetch_channel_id_for_author_patch.assert_called_with('testchannel')

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__fetch_existing_channel__based_on_channelid(
            self, fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = 1234
        Channel.objects.create(
            author='testchannel',
            title='Test Channel',
            channelid=1234,
        )

        form = AddChannelForm({
            'channel': 'sametestchannel',
        })

        self.assertFalse(form.is_valid())
        self.assertTrue('channel' in form.errors)
        self.assertEqual(form.errors['channel'][0],
                         'Channel already exists in the system '
                         'under the title: <b>Test Channel</b>')
        fetch_channel_id_for_author_patch.assert_called_with(
            'sametestchannel')

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    @mock.patch('youtube.forms.check_channel_id_exists')
    def test__channel_does_not_exist(
            self, check_channel_id_exists_patch,
            fetch_channel_id_for_author_patch):
        check_channel_id_exists_patch.return_value = False
        fetch_channel_id_for_author_patch.return_value = None

        form = AddChannelForm({
            'channel': 'testchannel',
        })

        self.assertFalse(form.is_valid())
        self.assertTrue('channel' in form.errors)
        self.assertEqual(form.errors['channel'][0],
                         'Channel does not seem to exist: <b>testchannel</b>')
        self.assertTrue(check_channel_id_exists_patch.called)
        self.assertTrue(fetch_channel_id_for_author_patch.called)

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    @mock.patch('youtube.forms.check_channel_id_exists')
    def test__channel_is_a_channelid(
            self, check_channel_id_exists_patch,
            fetch_channel_id_for_author_patch):
        check_channel_id_exists_patch.return_value = True
        fetch_channel_id_for_author_patch.return_value = None

        form = AddChannelForm({
            'channel': '1234',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['channelid'], '1234')
        self.assertTrue(check_channel_id_exists_patch.called)
        self.assertTrue(fetch_channel_id_for_author_patch.called)
