from django.test import TestCase

from ..templatetags.pretty_duration import pretty_duration


class PrettyDurationTest(TestCase):
    def test(self):
        self.assertEqual(pretty_duration(135.0), '02:15')

    def test__with_hour(self):
        self.assertEqual(pretty_duration(9313.0), '02:35:13')
