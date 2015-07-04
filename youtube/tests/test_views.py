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
