import logging

import mock
from django.test import TestCase
from django.core.management import call_command

from ..models import Channel, Video, Category


class UpdateChannelsTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(
            'youtube.management.commands.update_channels')
        self.logger.disabled = True

    def tearDown(self):
        self.logger.disabled = False

    def test__no_channels(self):
        call_command('update_channels')

    @mock.patch.object(Channel, 'update_channel_info')
    @mock.patch.object(Channel, 'fetch_videos')
    def test__single_channel__no_videos(self, fetch_videos_patch,
                                        update_channel_info_patch):
        Channel.objects.create()

        call_command('update_channels')

        self.assertTrue(fetch_videos_patch.called)
        self.assertTrue(update_channel_info_patch.called)

    @mock.patch.object(Channel, 'update_channel_info')
    @mock.patch.object(Channel, 'fetch_videos')
    def test__single_channel__no_videos__full_fetch(
            self, fetch_videos_patch, update_channel_info_patch):
        Channel.objects.create()

        call_command('update_channels', '--full')

        self.assertTrue(fetch_videos_patch.called)
        self.assertTrue(update_channel_info_patch.called)

    @mock.patch('youtube.management.commands.update_channels.requests')
    @mock.patch.object(Channel, 'update_channel_info')
    @mock.patch.object(Channel, 'fetch_videos')
    def test__no_channels__single_video__still_exists(
            self, fetch_videos_patch, update_channel_info_patch,
            requests_patch):
        requests_patch.head().status_code = 200
        Video.objects.create(
            category=Category.objects.create(
                id=1,
            ),
            uploader=Channel.objects.create(),
        )

        call_command('update_channels')

        self.assertTrue(requests_patch.head.called)

    @mock.patch('youtube.management.commands.update_channels.requests')
    @mock.patch.object(Channel, 'update_channel_info')
    @mock.patch.object(Channel, 'fetch_videos')
    def test__no_channels__single_video__not_found(
            self, fetch_videos_patch, update_channel_info_patch,
            requests_patch):
        requests_patch.head().status_code = 404
        video = Video.objects.create(
            category=Category.objects.create(
                id=1,
            ),
            uploader=Channel.objects.create(),
        )

        call_command('update_channels')

        self.assertTrue(requests_patch.head.called)
        video = Video.objects.get(pk=video.pk)
        self.assertTrue(video.deleted)

    @mock.patch('youtube.management.commands.update_channels.requests')
    @mock.patch.object(Channel, 'update_channel_info')
    @mock.patch.object(Channel, 'fetch_videos')
    def test__no_channels__single_video__weird_status_code(
            self, fetch_videos_patch, update_channel_info_patch,
            requests_patch):
        requests_patch.head().status_code = 500
        Video.objects.create(
            category=Category.objects.create(
                id=1,
            ),
            uploader=Channel.objects.create(),
        )

        call_command('update_channels')

        self.assertTrue(requests_patch.head.called)
        self.assertTrue(requests_patch.head().raise_for_status)
