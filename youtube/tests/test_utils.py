from __future__ import unicode_literals

import mock
from django.test import TestCase

from ..utils import does_channel_author_exist, calculate_rating


class DoesChannelAuthorExistTest(TestCase):
    @mock.patch('youtube.utils.requests')
    def test__channel_exists(self, requests_patch):
        requests_patch.get().json.return_value = {
            'pageInfo': {
                'totalResults': 1,
            }
        }

        self.assertTrue(does_channel_author_exist('testchannel'))

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)
        self.assertTrue(requests_patch.get().json.called)

    @mock.patch('youtube.utils.requests')
    def test__channel_does_not_exist(self, requests_patch):
        requests_patch.get().raise_for_status.side_effect = Exception(
            'failed request')

        with self.assertRaises(Exception):
            does_channel_author_exist('testchannel')

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)


class CalculateRatingTest(TestCase):
    def test__success(self):
        self.assertEqual(calculate_rating(200, 300), 2.0)

    def test__div_by_zero(self):
        self.assertIsNone(calculate_rating(0, 0))
