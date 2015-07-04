from __future__ import unicode_literals

import mock
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ..models import Channel


class IndexTest(TestCase):
    def test__get(self):
        resp = self.client.get(reverse('index'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')


class ChannelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            author='testauthor',
        )

    def test__get(self):
        resp = self.client.get(reverse('channel', kwargs={
            'author': self.channel.author,
        }))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')


class LoggedInTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('testuser', '', 'testpass')
        self.client.login(username='testuser', password='testpass')


class AdminTest(LoggedInTestCase):
    def test__get(self):
        resp = self.client.get(reverse('admin'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/admin.html')


class ChannelDeleteTest(LoggedInTestCase):
    def setUp(self):
        super(ChannelDeleteTest, self).setUp()
        self.channel = Channel.objects.create()

    @mock.patch('youtube.views.messages')
    def test__post(self, messages_patch):
        resp = self.client.post(reverse('channel-delete', kwargs={
            'channelid': self.channel.pk,
        }))

        self.assertRedirects(resp, reverse('admin'))
        self.assertFalse(Channel.objects.filter(pk=self.channel.pk).exists())
        self.assertTrue(messages_patch.success.called)


class ChannelAddTest(LoggedInTestCase):
    @mock.patch('youtube.views.messages')
    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__post__success(self, does_channel_author_exist_patch,
                            messages_patch):
        does_channel_author_exist_patch.return_value = True

        with mock.patch.object(Channel,
                          'update_channel_info') as channel_info_patch,\
                mock.patch.object(Channel, 'fetch_videos') as fetch_videos_patch:

            resp = self.client.post(reverse('channel-add'), {
                'channel': 'testchannel',
            })

            self.assertTrue(channel_info_patch.called)
            self.assertTrue(fetch_videos_patch.called)

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)
        self.assertTrue(does_channel_author_exist_patch.called)
        self.assertTrue(Channel.objects.filter(author='testchannel').exists())

    @mock.patch('youtube.forms.does_channel_author_exist')
    def test__post__does_not_exist(self, does_channel_author_exist_patch):
        does_channel_author_exist_patch.return_value = False

        resp = self.client.post(reverse('channel-add'), {
            'channel': 'testchannel',
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/admin.html')
        self.assertFormError(
            resp, 'form', 'channel',
            'Channel does not seem to exist: <b>testchannel</b>')
        self.assertTrue(does_channel_author_exist_patch.called)
