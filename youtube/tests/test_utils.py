from __future__ import unicode_literals

import mock
from django.test import TestCase

from ..utils import (
    calculate_rating,
    check_channel_id_exists,
    fetch_channel_id_for_author,
)


class FetchChannelIdForAuthorTest(TestCase):
    @mock.patch('youtube.utils.requests')
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

    @mock.patch('youtube.utils.requests')
    def test__channel_does_not_exist(self, requests_patch):
        requests_patch.get().raise_for_status.side_effect = Exception(
            'failed request')

        with self.assertRaises(Exception):
            fetch_channel_id_for_author('testchannel')

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)


class CheckChannelIdExists(TestCase):
    @mock.patch('youtube.utils.requests')
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

    @mock.patch('youtube.utils.requests')
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


class CalculateRatingTest(TestCase):
    def test__success(self):
        self.assertEqual(calculate_rating(200, 300), 2.0)

    def test__div_by_zero(self):
        self.assertIsNone(calculate_rating(0, 0))
