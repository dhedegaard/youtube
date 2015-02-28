import datetime

import requests
import dateutil.parser
from django.db import models
from django.utils import timezone


class Channel(models.Model):
    author = models.TextField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'id: %s, author: %s' % (
            self.id,
            self.author,
        )

    def fetch(self, force=False):
        resp = requests.get(
            'https://gdata.youtube.com/feeds/api/videos?'
            'author=%s&v=2&orderby=updated&alt=jsonc' % self.author
        )
        for row in resp.json()['data']['items']:
            Video.objects.create_or_update(self, row)

    @property
    def url(self):
        return u'https://www.youtube.com/user/%(author)s/videos' % {
            'author': self.author,
        }

class Category(models.Model):
    category = models.TextField(unique=True)

    def __unicode__(self):
        return unicode(self.category)


class VideoQuerySet(models.QuerySet):
    def create_or_update(self, channel, row):
        youtubeid = row['id']
        video = Video.objects.filter(youtubeid=youtubeid).first()

        if not video:
            category = Category.objects.get_or_create(
                category=row['category'],
            )[0]
            # Create the video.
            video = Video.objects.create(
                youtubeid=youtubeid,
                uploader=channel,
                title=row['title'],
                category=category,
                description=row['description'],
                duration=row['duration'],
                rating=row['rating'],
                like_count=row['likeCount'],
                rating_count=row['ratingCount'],
                view_count=row['viewCount'],
                favorite_count=row['favoriteCount'],
                comment_count=row['commentCount'],
                uploaded=dateutil.parser.parse(row['uploaded']),
                updated=dateutil.parser.parse(row['updated']),
            )
        return video



class Video(models.Model):
    objects = VideoQuerySet.as_manager()

    youtubeid = models.TextField(unique=True)
    uploader = models.ForeignKey(Channel, related_name='videos')
    title = models.TextField(default='')
    description = models.TextField(default='')
    duration = models.IntegerField(default=0)  # in seconds
    category = models.ForeignKey(Category, related_name='videos')
    rating = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    rating_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    uploaded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()

    class Meta:
        ordering = ['-uploaded']

    def get_thumbnail(self, quality='hqdefault'):
        return 'https://i.ytimg.com/vi/%(youtubeid)s/%(quality)s.jpg' % {
            'youtubeid': self.youtubeid,
            'quality': quality,
        }

    @property
    def url(self):
        return 'https://www.youtube.com/watch?v=%(youtubeid)s' % {
            'youtubeid': self.youtubeid,
        }

    def __unicode__(self):
        return unicode(self.youtubeid)
