from django.test import TestCase

from ..templatetags.pretty_duration import pretty_duration

class PrettyDurationTest(TestCase):
    def test(self):
        self.assertEqual(pretty_duration(135.0), '02:15')
