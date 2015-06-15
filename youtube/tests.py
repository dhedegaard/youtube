from django.test import TestCase
from django.core.urlresolvers import reverse


class IndexTest(TestCase):
    def test_get(self):
        resp = self.client.get(reverse('index'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'youtube/index.html')
