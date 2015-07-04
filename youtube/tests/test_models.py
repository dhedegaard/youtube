import mock
from django.test import TestCase

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
