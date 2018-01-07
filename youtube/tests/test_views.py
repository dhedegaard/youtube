from __future__ import unicode_literals

import mock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Channel


class LoggedInTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('testuser', '', 'testpass')
        self.client.login(username='testuser', password='testpass')


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

    def test__get__hidden_not_logged_in(self):
        self.channel.hidden = True
        self.channel.save()

        resp = self.client.get(reverse('channel', kwargs={
            'author': self.channel.author,
        }))

        self.assertEqual(resp.status_code, 404)

    def test__get__hidden_logged_in(self):
        self.channel.hidden = True
        self.channel.save()
        User.objects.create_superuser('testuser', '', 'testpass')
        self.client.login(username='testuser', password='testpass')

        resp = self.client.get(reverse('channel', kwargs={
            'author': self.channel.author,
        }))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')


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
    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    def test__post__success(self, fetch_channel_id_for_author_patch,
                            messages_patch):
        fetch_channel_id_for_author_patch.return_value = 1234

        with mock.patch.object(
                Channel, 'update_channel_info') as channel_info_patch,\
            mock.patch.object(
                Channel, 'fetch_videos') as fetch_videos_patch:

            resp = self.client.post(reverse('channel-add'), {
                'channel': 'testchannel',
            })

            self.assertTrue(channel_info_patch.called)
            self.assertTrue(fetch_videos_patch.called)

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)
        self.assertTrue(fetch_channel_id_for_author_patch.called)
        channel = Channel.objects.filter(author='testchannel').first()
        self.assertIsNotNone(channel)
        self.assertEqual(channel.channelid, '1234')

    @mock.patch('youtube.forms.fetch_channel_id_for_author')
    @mock.patch('youtube.forms.check_channel_id_exists')
    def test__post__does_not_exist(
            self, check_channel_id_exists_patch,
            fetch_channel_id_for_author_patch):
        fetch_channel_id_for_author_patch.return_value = False
        check_channel_id_exists_patch.return_value = False

        resp = self.client.post(reverse('channel-add'), {
            'channel': 'testchannel',
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/admin.html')
        self.assertFormError(
            resp, 'form', 'channel',
            'Channel does not seem to exist: <b>testchannel</b>')
        self.assertTrue(fetch_channel_id_for_author_patch.called)
        self.assertTrue(check_channel_id_exists_patch.called)


class ToggleHiddenTest(LoggedInTestCase):
    def setUp(self):
        super(ToggleHiddenTest, self).setUp()
        self.channel = Channel.objects.create(
            author='testchannel',
        )

    @mock.patch('youtube.views.messages')
    def test__post__set_hidden(self, messages_patch):
        resp = self.client.post(reverse('toggle-hidden', kwargs={
            'channelid': self.channel.pk,
        }))

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)
        channel = Channel.objects.get(pk=self.channel.pk)
        self.assertTrue(channel.hidden)

    @mock.patch('youtube.views.messages')
    def test__post__unset_hidden(self, messages_patch):
        self.channel.hidden = True
        self.channel.save()

        resp = self.client.post(reverse('toggle-hidden', kwargs={
            'channelid': self.channel.pk,
        }))

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)
        channel = Channel.objects.get(pk=self.channel.pk)
        self.assertFalse(channel.hidden)


class ChannelFullFetchTest(LoggedInTestCase):
    def setUp(self):
        super(ChannelFullFetchTest, self).setUp()
        self.channel = Channel.objects.create(
            author='testauthor',
            title='testtitle',
        )

    @mock.patch('youtube.views.messages')
    def test__post__success(self, messages_patch):
        with mock.patch.object(
                Channel, 'update_channel_info') as channel_info_patch,\
            mock.patch.object(
                Channel, 'fetch_videos') as fetch_videos_patch:

            resp = self.client.post(reverse('channel-full-fetch', kwargs={
                'channelid': self.channel.pk,
            }))

            self.assertTrue(channel_info_patch.called)
            self.assertTrue(fetch_videos_patch.called)
            self.assertEqual(fetch_videos_patch.call_args,
                             mock.call(full_fetch=True))

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)


class ChannelFetchTest(LoggedInTestCase):
    def setUp(self):
        super(ChannelFetchTest, self).setUp()
        self.channel = Channel.objects.create(
            author='testauthor',
            title='testtitle',
        )

    @mock.patch('youtube.views.messages')
    def test__post__success(self, messages_patch):
        with mock.patch.object(
                Channel, 'update_channel_info') as channel_info_patch,\
            mock.patch.object(
                Channel, 'fetch_videos') as fetch_videos_patch:

            resp = self.client.post(reverse('channel-fetch', kwargs={
                'channelid': self.channel.pk,
            }))

            self.assertTrue(channel_info_patch.called)
            self.assertTrue(fetch_videos_patch.called)
            self.assertEqual(fetch_videos_patch.call_args,
                             mock.call(full_fetch=False))

        self.assertRedirects(resp, reverse('admin'))
        self.assertTrue(messages_patch.success.called)
