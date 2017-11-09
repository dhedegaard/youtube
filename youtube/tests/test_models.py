from __future__ import unicode_literals
import datetime
import mock

import pytz
from django.test import TestCase
from django.utils import timezone

from ..models import Channel, Category, Video


class ChannelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            author='testauthor',
        )

    @mock.patch('youtube.models.fetch_channel_info')
    def test__update_channel_info(self, fetch_channel_info_patch):
        fetch_channel_info_patch.return_value = {
            'snippet': {
                'title': 'testchannel',
                'thumbnails': {
                    'default': {
                        'url': 'http://example.com/image.png',
                    },
                },
            },
            'contentDetails': {
                'relatedPlaylists': {
                    'uploads': 'uploadschannelid',
                },
            },
        }

        self.channel.update_channel_info()

        self.channel.refresh_from_db()
        self.assertEqual(self.channel.title, 'testchannel')
        self.assertEqual(
            self.channel.thumbnail, 'http://example.com/image.png')
        self.assertEqual(self.channel.uploads_playlist, 'uploadschannelid')
        fetch_channel_info_patch.assert_called_with(self.channel.channelid)

    @mock.patch('youtube.models.fetch_channel_info')
    def test__update_channel_info__no_save(self, fetch_channel_info_patch):
        fetch_channel_info_patch.return_value = {
            'snippet': {
                'title': 'testchannel',
                'thumbnails': {
                    'default': {
                        'url': 'http://example.com/image.png',
                    },
                },
            },
            'contentDetails': {
                'relatedPlaylists': {
                    'uploads': 'uploadschannelid',
                },
            },
        }

        self.channel.update_channel_info(save=False)

        self.assertEqual(self.channel.title, 'testchannel')
        self.assertEqual(self.channel.thumbnail,
                         'http://example.com/image.png')
        self.assertEqual(self.channel.uploads_playlist, 'uploadschannelid')
        fetch_channel_info_patch.assert_called_with(self.channel.channelid)

    @mock.patch('youtube.models.fetch_videos')
    @mock.patch('youtube.models.fetch_videos_from_playlist')
    @mock.patch.object(Category.objects, 'get_categoryids')
    @mock.patch.object(Video.objects, 'create_or_update')
    def test__fetch_videos(
            self, create_or_update_patch,
            get_categoryids_patch,
            fetch_videos_from_playlist_patch,
            fetch_videos_patch):
        fetch_videos_from_playlist_patch.return_value = [{
            'snippet': {
                'categoryId': 1,
            },
            'contentDetails': {
                'videoId': 'abcdef',
            },
        }], None
        fetch_videos_patch.return_value = [{
            'snippet': {
                'categoryId': 1,
            },
            'contentDetails': {
                'videoId': 'abcdef',
            },
        }]

        self.channel.fetch_videos()

        self.assertTrue(get_categoryids_patch.called)
        self.assertTrue(create_or_update_patch.called)
        fetch_videos_from_playlist_patch.assert_called_with(
            self.channel.channelid, next_page_token=None)
        fetch_videos_patch.assert_called_with({'abcdef'})

    @mock.patch('youtube.models.fetch_videos')
    @mock.patch('youtube.models.fetch_videos_from_playlist')
    @mock.patch.object(Category.objects, 'get_categoryids')
    @mock.patch.object(Video.objects, 'create_or_update')
    def test__fetch_videos__full_fetch(
            self, create_or_update_patch,
            get_categoryids_patch,
            fetch_videos_from_playlist_patch,
            fetch_videos_patch):
        fetch_videos_from_playlist_patch.return_value = [{
            'snippet': {
                'categoryId': 1,
            },
            'contentDetails': {
                'videoId': 'abcdef',
            },
        }], None
        fetch_videos_patch.return_value = [{
            'snippet': {
                'categoryId': 1,
            },
            'contentDetails': {
                'videoId': 'abcdef',
            },
        }]

        self.channel.fetch_videos(full_fetch=True)

        self.assertTrue(get_categoryids_patch.called)
        self.assertTrue(create_or_update_patch.called)
        fetch_videos_from_playlist_patch.assert_called_with(
            self.channel.channelid, next_page_token=None)
        fetch_videos_patch.assert_called_with({'abcdef'})


class CategoryQuerySetTest(TestCase):
    def test__empty_ids(self):
        self.assertEqual(len(Category.objects.get_categoryids([])), 0)

    def test__existing_categories(self):
        category = Category.objects.create(
            pk=1,
            category='testcategory',
        )

        result = Category.objects.get_categoryids([1])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], category)

    @mock.patch('youtube.models.fetch_videocategories')
    def test__new_category(self, fetch_videocategories_patch):
        fetch_videocategories_patch.return_value = [
            {
                'id': 1,
                'snippet': {
                    'title': 'testcategory',
                },
            },
        ]
        result = Category.objects.get_categoryids([1])

        self.assertEqual(Category.objects.all().count(), 1)
        self.assertTrue(Category.objects.filter(pk=1).exists())
        self.assertEqual(result[0].pk, 1)
        self.assertEqual(result[0].category, 'testcategory')
        fetch_videocategories_patch.assert_called_with({1})


class VideoQuerySetTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            author='testchannel',
        )
        self.category = Category.objects.create(
            pk=1,
            category='testcategory',
        )
        self.videodata = {
            'id': 'abcdef',
            'statistics': {
                'viewCount': 1000,
                'favoriteCount': 20,
            },
            'contentDetails': {
                'duration': 'PT3M40S',
            },
            'snippet': {
                'title': 'testvideo',
                'categoryId': 1,
                'description': 'testdescription',
                'publishedAt': '2014-01-01T12:00:00.000Z',
            },
        }

    def test__create_or_update__new_video(self):
        video = Video.objects.create_or_update(self.channel, self.videodata)

        uploaded = timezone.make_aware(
            datetime.datetime(2014, 1, 1, 12), timezone.get_current_timezone())

        video.refresh_from_db()
        self.assertEqual(video.duration, 3 * 60 + 40)
        self.assertEqual(video.uploader, self.channel)
        self.assertEqual(video.category, self.category)
        self.assertEqual(video.view_count, 1000)
        self.assertEqual(video.favorite_count, 20)
        self.assertEqual(video.uploaded.astimezone(pytz.utc),
                         uploaded.astimezone(pytz.utc))
        self.assertEqual(video.updated, uploaded)

    def test__create_or_update__existing_video(self):
        video = Video.objects.create(
            youtubeid='abcdef',
            category=self.category,
            uploader=self.channel,
            duration=123,
        )

        video = Video.objects.create_or_update(self.channel, self.videodata)

        uploaded = timezone.make_aware(
            datetime.datetime(2014, 1, 1, 12), timezone.get_current_timezone())

        video.refresh_from_db()
        self.assertEqual(video.duration, 3 * 60 + 40)
        self.assertEqual(video.uploader, self.channel)
        self.assertEqual(video.category, self.category)
        self.assertEqual(video.view_count, 1000)
        self.assertEqual(video.favorite_count, 20)
        self.assertIsNotNone(video.uploaded)
        self.assertEqual(video.updated.astimezone(pytz.utc),
                         uploaded.astimezone(pytz.utc))
