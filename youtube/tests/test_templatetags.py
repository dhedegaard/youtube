from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.test import TestCase
from freezegun import freeze_time

from ..templatetags.pretty_duration import pretty_duration
from ..templatetags.youtubetags import timesince_short


class PrettyDurationTest(TestCase):
    def test(self):
        self.assertEqual(pretty_duration(135.0), '02:15')

    def test__with_hour(self):
        self.assertEqual(pretty_duration(9313.0), '02:35:13')


@freeze_time('2000-01-01')
class TimesinceShortTest(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test__bad_type(self):
        with self.assertRaises(TypeError):
            timesince_short('random string')

    def test__more_than_one_year_ago(self):
        self.assertEqual(
            u'2y0m ago', timesince_short(
                self.now - relativedelta(years=2)))

    def test__more_than_one_month_ago(self):
        self.assertEqual(
            u'2m0D ago', timesince_short(
                self.now - relativedelta(months=2)))

    def test__more_than_one_day_ago(self):
        self.assertEqual(
            u'2D0h ago', timesince_short(
                self.now - relativedelta(days=2)))

    def test__hours_and_minutes(self):
        self.assertEqual(
            u'2h4m ago', timesince_short(
                self.now - relativedelta(hours=2, minutes=4)))
