from __future__ import unicode_literals

import mock
from django.test import TestCase
from django.conf import settings

from ..youtubeapi import (
    check_channel_id_exists,
    fetch_channel_id_for_author,
    fetch_channel_info,
    fetch_videocategories,
    fetch_videos_from_playlist,
    fetch_videos,
)


class FetchChannelIdForAuthorTest(TestCase):
    @mock.patch('youtube.youtubeapi.requests')
    def test__channel_exists(self, requests_patch):
        requests_patch.get().json.return_value = {
            'pageInfo': {
                'totalResults': 1,
            },
            'items': [
                {
                    'id': 1234,
                },
            ],
        }

        self.assertEqual(
            1234, fetch_channel_id_for_author('testchannel'))

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)
        self.assertTrue(requests_patch.get().json.called)

    @mock.patch('youtube.youtubeapi.requests')
    def test__channel_does_not_exist(self, requests_patch):
        requests_patch.get().raise_for_status.side_effect = Exception(
            'failed request')

        with self.assertRaises(Exception):
            fetch_channel_id_for_author('testchannel')

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)


class CheckChannelIdExists(TestCase):
    @mock.patch('youtube.youtubeapi.requests')
    def test__exists(self, requests_patch):
        resp_mock = mock.MagicMock()
        resp_mock.json.return_value = {
            'pageInfo': {
                'totalResults': 1,
            },
        }
        requests_patch.get.return_value = resp_mock

        self.assertTrue(check_channel_id_exists('testchannel'))

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)

    @mock.patch('youtube.youtubeapi.requests')
    def test__does_not_exist(self, requests_patch):
        resp_mock = mock.MagicMock()
        resp_mock.json.return_value = {
            'pageInfo': {
                'totalResults': 0,
            },
        }
        requests_patch.get.return_value = resp_mock

        self.assertFalse(check_channel_id_exists('testchannel'))

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)


class FetchVideocategoriesTestCase(TestCase):

    @mock.patch('youtube.youtubeapi.requests')
    def test(self, requests_patch):
        resp_mock = mock.Mock()
        resp_mock.json.return_value = {
            'items': [
                {
                    'name': 'item1',
                },
            ],
        }
        requests_patch.get.return_value = resp_mock

        self.assertEqual(fetch_videocategories([1, 2, 3]), [
            {
                'name': 'item1',
            },
        ])

        requests_patch.get.assert_called_with(
            'https://www.googleapis.com/youtube/v3/videoCategories',
            params={
                'part': 'snippet',
                'id': '1,2,3',
                'key': settings.YOUTUBE_API_KEY,
            })
        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)


class FetchChannelInfoTestCase(TestCase):

    @mock.patch('youtube.youtubeapi.requests')
    def test(self, requests_patch):
        resp_mock = mock.Mock()
        resp_mock.json.return_value = {
            'items': [
                {
                    'id': '1234',
                },
            ],
        }
        requests_patch.get.return_value = resp_mock

        self.assertEqual(fetch_channel_info('1234'), {
            'id': '1234',
        })

        requests_patch.get.assert_called_with(
            'https://www.googleapis.com/youtube/v3/channels', params={
                'part': 'snippet,contentDetails',
                'id': '1234',
                'key': settings.YOUTUBE_API_KEY,
            })
        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)


class FetchVideosFromPlaylistTestCase(TestCase):

    @mock.patch('youtube.youtubeapi.requests')
    def test(self, requests_patch):
        resp_mock = mock.Mock()
        resp_mock.json.return_value = {
            'nextPageToken': 'nextpagetoken',
            'items': [
                {
                    'videoid': '1234',
                },
            ],
        }
        requests_patch.get.return_value = resp_mock

        self.assertEqual(fetch_videos_from_playlist('abc'), (
            [
                {
                    'videoid': '1234',
                }
            ],
            'nextpagetoken',
        ))

        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)
        requests_patch.get.assert_called_with(
            'https://www.googleapis.com/youtube/v3/playlistItems', params={
                'part': 'contentDetails',
                'maxResults': 50,
                'playlistId': 'abc',
                'key': settings.YOUTUBE_API_KEY,
                'pageToken': None,
            }
        )


class FetchVideosTestCase(TestCase):

    @mock.patch('youtube.youtubeapi.requests')
    def test(self, requests_patch):
        resp_mock = mock.Mock()
        resp_mock.json.return_value = {
            'items': [
                {
                    'videoid': '1234',
                },
            ],
        }
        requests_patch.get.return_value = resp_mock

        self.assertEqual(fetch_videos({'abc', 'def'}), [
            {
                'videoid': '1234',
            },
        ])

        requests_patch.get.assert_called_with(
            'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet,contentDetails,statistics',
                'id': ','.join({'abc', 'def'}),
                'key': settings.YOUTUBE_API_KEY,
            })
        self.assertTrue(resp_mock.raise_for_status.called)
        self.assertTrue(resp_mock.json.called)
