from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Channel


class IndexTest(TestCase):
    def test__get(self):
        resp = self.client.get(reverse('index'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')


class ChannelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            author='testauthor',
        )

    def test__get(self):
        resp = self.client.get(reverse('channel', kwargs={
            'author': self.channel.author,
        }))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')
