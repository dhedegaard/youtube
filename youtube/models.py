from __future__ import unicode_literals

import dateutil.parser
from django.db import models
from django.utils import timezone
from isodate import parse_duration

from .youtubeapi import (
    fetch_channel_info,
    fetch_videocategories,
    fetch_videos_from_playlist,
    fetch_videos,
)


class Channel(models.Model):
    channelid = models.TextField(unique=True)
    author = models.TextField(unique=True, null=True)
    title = models.TextField(default='', db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False, db_index=True)
    thumbnail = models.TextField(default='')
    uploads_playlist = models.TextField(default='')

    def __unicode__(self):
        return 'id: %s, author: %s' % (
            self.id,
            self.author,
        )

    def update_channel_info(self, save=True):
        # Retrieve the channel info.
        info = fetch_channel_info(self.channelid)

        # Save details from channel.
        self.title = info['snippet']['title']
        self.thumbnail = info['snippet']['thumbnails']['default']['url']
        self.uploads_playlist = (
            info['contentDetails']['relatedPlaylists']['uploads'])

        if save:
            self.save()

    def fetch_videos(self, full_fetch=False):
        '''
        Fetch new videos from the channel.

        If full_fetch is True all videos for the given channel is fetched.

        Returns the number of videos fetched (if any).
        '''
        fetched = 0

        next_page_token = None
        content_exists = True

        while content_exists:
            # Read response as JSON and fetch all videoids.
            items, next_page_token = fetch_videos_from_playlist(
                self.uploads_playlist, next_page_token=next_page_token)
            videoids = set(
                [item['contentDetails']['videoId'] for item in items])

            # Fetch the next page token, if it exists and the callers wants it.
            if not full_fetch or not next_page_token:
                content_exists = False

            # Not fetch videodata based on the video ids.
            items = fetch_videos(videoids)

            # Create all categories used, and not already in the backend.
            Category.objects.get_categoryids([
                e['snippet']['categoryId'] for e in items])

            # Read response as JSON and iterate on items updating/creating
            # Video objects as we go along.
            for item in items:
                fetched += 1
                Video.objects.create_or_update(self, item)

        # All done, return the number of videos fetched.
        return fetched

    @property
    def url(self):
        return 'https://www.youtube.com/user/%(author)s/videos' % {
            'author': self.author,
        }


class CategoryQuerySet(models.QuerySet):
    def get_categoryids(self, categoryids):
        '''
        Fetches and returns a list of categories, creates categories that does
        not already exist.

        Internally the category is attempted fetched from the backend, if it
        does not exist a query against the youtube API is executed to fetch and
        create a new `Category` object.
        '''
        # Fetch existing categories from the backend.
        categories = self.filter(id__in=categoryids)
        existing_categoryids = categories.values_list('pk', flat=True)

        # Figure out what we're missing (if we're missing anything).
        missing_categoryids = set([
            e for e in categoryids if e not in existing_categoryids])

        # Fetch missing categories and create them in the backend.
        if missing_categoryids:

            # Iterate and create new categories, adding them to the existing
            # list of categories.
            categories = list(categories)
            for item in fetch_videocategories(missing_categoryids):
                categories.append(self.get_or_create(
                    id=item['id'],
                    defaults={
                        'category': item['snippet']['title'],
                    })[0])

        return categories


class Category(models.Model):
    objects = CategoryQuerySet.as_manager()

    id = models.IntegerField(primary_key=True)
    category = models.TextField(unique=True)

    def __unicode__(self):
        return self.category


class VideoQuerySet(models.QuerySet):

    def exclude_deleted(self):
        return self.exclude(deleted=True)

    def create_or_update(self, channel, data):
        '''
        Creates or updates a `Video` object with the data given, for the
        channel given.
        '''
        # Fetch video details, if it exists.
        duration = parse_duration(data['contentDetails']['duration'])

        return Video.objects.update_or_create(
            youtubeid=data['id'],
            defaults={
                'uploader': channel,
                'title': data['snippet']['title'],
                'category_id': data['snippet']['categoryId'],
                'description': data['snippet']['description'],
                'duration': duration.total_seconds(),
                'view_count': data.get('statistics', {}).get('viewCount'),
                'favorite_count': data.get(
                    'statistics', {}).get('favoriteCount'),
                'uploaded': dateutil.parser.parse(
                    data['snippet']['publishedAt']),
                'updated': dateutil.parser.parse(
                    data['snippet']['publishedAt']),
            },
        )[0]


class Video(models.Model):
    objects = VideoQuerySet.as_manager()

    youtubeid = models.TextField(unique=True)
    uploader = models.ForeignKey(
        Channel, related_name='videos', on_delete=models.CASCADE)
    title = models.TextField(default='')
    duration = models.IntegerField(default=0)  # in seconds
    category = models.ForeignKey(
        Category, related_name='videos', on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0, null=True)
    favorite_count = models.IntegerField(default=0, null=True)
    uploaded = models.DateTimeField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()
    description = models.TextField(default='')
    deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-uploaded']

    def get_thumbnail(self, quality='hqdefault'):
        return 'https://i.ytimg.com/vi/%(youtubeid)s/%(quality)s.jpg' % {
            'youtubeid': self.youtubeid,
            'quality': quality,
        }

    @property
    def url(self):  # pragma: nocover
        return 'https://www.youtube.com/watch?v=%(youtubeid)s' % {
            'youtubeid': self.youtubeid,
        }

    def __unicode__(self):
        return str(self.youtubeid)

    def save(self, *args, **kwargs):
        if not self.uploaded:
            self.uploaded = timezone.now()

        if not self.updated:
            self.updated = self.uploaded

        super(Video, self).save(*args, **kwargs)
