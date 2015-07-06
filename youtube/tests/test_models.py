from __future__ import unicode_literals
import datetime
from decimal import Decimal

import mock
from django.test import TestCase
from django.utils import timezone

from ..models import Channel, Category, Video


class ChannelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            author='testauthor',
        )

    @mock.patch('youtube.models.requests')
    def test__update_channel_info(self, requests_patch):
        requests_patch.get().json.return_value = {
            'items': [{
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
            }],
        }

        self.channel.update_channel_info()

        channel = Channel.objects.get(pk=self.channel.pk)
        self.assertEqual(channel.title, 'testchannel')
        self.assertEqual(channel.thumbnail, 'http://example.com/image.png')
        self.assertEqual(channel.uploads_playlist, 'uploadschannelid')
        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status)

    @mock.patch('youtube.models.requests')
    def test__update_channel_info__no_save(self, requests_patch):
        requests_patch.get().json.return_value = {
            'items': [{
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
            }],
        }

        self.channel.update_channel_info(save=False)

        channel = Channel.objects.get(pk=self.channel.pk)
        self.assertEqual(self.channel.title, 'testchannel')
        self.assertEqual(self.channel.thumbnail,
                         'http://example.com/image.png')
        self.assertEqual(self.channel.uploads_playlist, 'uploadschannelid')
        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status)

    @mock.patch('youtube.models.requests')
    @mock.patch.object(Category.objects, 'get_categoryids')
    @mock.patch.object(Video.objects, 'create_or_update')
    def test__fetch_videos(self, create_or_update_patch,
                           get_categoryids_patch, requests_patch):
        requests_patch.get().json.return_value = {
            'items': [{
                'snippet': {
                    'categoryId': 1,
                },
                'contentDetails': {
                    'videoId': 'abcdef',
                },
            }],
        }

        self.channel.fetch_videos()

        self.assertTrue(get_categoryids_patch.called)
        self.assertTrue(create_or_update_patch.called)
        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)
        self.assertTrue(requests_patch.get().json.called)


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

    @mock.patch('youtube.models.requests')
    def test__new_category(self, requests_patch):
        requests_patch.get().json.return_value = {
            'items': [
                {
                    'id': 1,
                    'snippet': {
                        'title': 'testcategory',
                    },
                },
            ],
        }
        result = Category.objects.get_categoryids([1])

        self.assertEqual(Category.objects.all().count(), 1)
        self.assertTrue(Category.objects.filter(pk=1).exists())
        self.assertEqual(result[0].pk, 1)
        self.assertEqual(result[0].category, 'testcategory')


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
                'likeCount': 200,
                'dislikeCount': 250,
                'viewCount': 1000,
                'favoriteCount': 20,
                'commentCount': 15,
            },
            'contentDetails': {
                'duration': 'PT3M40S',
            },
            'snippet': {
                'title': 'testvideo',
                'categoryId': 1,
                'description': 'testdescription',
                'publishedAt': '2014-01-01 12:00',
            },
        }

    def test__create_or_update__new_video(self):
        Video.objects.create_or_update(self.channel, self.videodata)
        uploaded = timezone.make_aware(datetime.datetime(2014, 1, 1, 12))

        self.assertTrue(Video.objects.filter(youtubeid='abcdef').exists())
        video = Video.objects.get(youtubeid='abcdef')
        self.assertEqual(video.rating, Decimal('2.2'))
        self.assertEqual(video.duration, 3 * 60 + 40)
        self.assertEqual(video.uploader, self.channel)
        self.assertEqual(video.category, self.category)
        self.assertEqual(video.like_count, 200)
        self.assertEqual(video.view_count, 1000)
        self.assertEqual(video.favorite_count, 20)
        self.assertEqual(video.comment_count, 15)
        self.assertEqual(video.uploaded, uploaded)
        self.assertEqual(video.updated, uploaded)

    def test__create_or_update__existing_video(self):
        video = Video.objects.create(
            youtubeid='abcdef',
            category=self.category,
            uploader=self.channel,
            duration=123,
        )

        Video.objects.create_or_update(self.channel, self.videodata)
        uploaded = timezone.make_aware(datetime.datetime(2014, 1, 1, 12))

        self.assertTrue(Video.objects.filter(youtubeid='abcdef').exists())
        video = Video.objects.get(youtubeid='abcdef')
        self.assertEqual(video.rating, Decimal('2.2'))
        self.assertEqual(video.duration, 123)
        self.assertEqual(video.uploader, self.channel)
        self.assertEqual(video.category, self.category)
        self.assertEqual(video.like_count, 200)
        self.assertEqual(video.view_count, 1000)
        self.assertEqual(video.favorite_count, 20)
        self.assertEqual(video.comment_count, 15)
        self.assertIsNotNone(video.uploaded)
        self.assertEqual(video.updated, uploaded)
