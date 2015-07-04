from __future__ import unicode_literals

import mock
from django.test import TestCase

from ..utils import does_channel_author_exist


class DoesChannelAuthorExistTest(TestCase):
    @mock.patch('youtube.utils.requests')
    def test__channel_exists(self, requests_patch):
        requests_patch.json.return_value = {
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
        requests_patch.raise_for_status.side_effect = Exception(
            'failed request')

        with self.assertRaises(Exception):
            does_channel_author_exist('testchannel')

        self.assertTrue(requests_patch.get.called)
        self.assertTrue(requests_patch.get().raise_for_status.called)
