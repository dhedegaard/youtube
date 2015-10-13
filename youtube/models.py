from __future__ import unicode_literals
import requests

import dateutil.parser
from django.db import models
from django.conf import settings
from django.utils import timezone
from isodate import parse_duration


class Channel(models.Model):
    author = models.TextField(unique=True)
    title = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', related_name='channels')
    thumbnail = models.TextField(default='')
    uploads_playlist = models.TextField(default='')

    def __unicode__(self):
        return 'id: %s, author: %s' % (
            self.id,
            self.author,
        )

    def update_channel_info(self, save=True):
        # Fetch data from the API.
        resp = requests.get(
            'https://www.googleapis.com/youtube/v3/channels', params={
                'part': 'snippet,contentDetails',
                'forUsername': self.author,
                'key': settings.YOUTUBE_API_KEY,
            }
        )
        resp.raise_for_status()

        # Read response as JSON and fetch the first item.
        data = resp.json()
        item = data['items'][0]

        # Save details from channel.
        self.title = item['snippet']['title']
        self.thumbnail = item['snippet']['thumbnails']['default']['url']
        self.uploads_playlist = (item['contentDetails']['relatedPlaylists']
                                 ['uploads'])

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
            # Fetch playlist-data from the API.
            resp = requests.get(
                'https://www.googleapis.com/youtube/v3/playlistItems', params={
                    'part': 'contentDetails',
                    'maxResults': 50,
                    'playlistId': self.uploads_playlist,
                    'key': settings.YOUTUBE_API_KEY,
                    'pageToken': next_page_token
                }
            )
            resp.raise_for_status()

            # Read response as JSON and fetch all videoids.
            data = resp.json()
            videoids = set(
                [item['contentDetails']['videoId'] for item in data['items']]
            )

            # Fetch the next page token, if it exists.
            if full_fetch:
                next_page_token = data.get('nextPageToken')
                content_exists = bool(next_page_token)
            else:
                content_exists = False

            # Fetch data for the videoids from previous playlist call(s), since
            # playlist doesn't return all the data we need.
            resp = requests.get(
                'https://www.googleapis.com/youtube/v3/videos', params={
                    'part': 'snippet,contentDetails,statistics',
                    'id': ','.join(videoids),
                    'key': settings.YOUTUBE_API_KEY,
                }
            )
            resp.raise_for_status()
            data = resp.json()

            # Create all categories used, and not already in the backend.
            Category.objects.get_categoryids([
                e['snippet']['categoryId'] for e in data['items']])

            # Read response as JSON and iterate on items updating/creating
            # Video objects as we go along.
            for item in data['items']:
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
        missing_categoryids = [e for e in categoryids
                               if e not in existing_categoryids]

        # Fetch missing categories and create them in the backend.
        if missing_categoryids:
            resp = requests.get(
                'https://www.googleapis.com/youtube/v3/videoCategories',
                params={
                    'part': 'snippet',
                    'id': ','.join([str(e) for e in missing_categoryids]),
                    'key': settings.YOUTUBE_API_KEY,
                })
            resp.raise_for_status()

            # Iterate and create new categories, adding them to the existing
            # list of categories.
            categories = list(categories)
            for item in resp.json()['items']:
                categories.append(self.get_or_create(
                    id=item['id'], category=item['snippet']['title'])[0])

        return categories


class Category(models.Model):
    objects = CategoryQuerySet.as_manager()

    id = models.IntegerField(primary_key=True)
    category = models.TextField(unique=True)

    def __unicode__(self):
        return unicode(self.category)


class VideoQuerySet(models.QuerySet):
    def exclude_deleted(self):
        return self.exclude(deleted=True)

    def create_or_update(self, channel, data):
        # Fetch video details, if it exists.
        youtubeid = data['id']
        video = Video.objects.filter(youtubeid=youtubeid).first()
        duration = parse_duration(data['contentDetails']['duration'])

        if not video:
            # Create the video.
            video = Video.objects.create(
                youtubeid=youtubeid,
                uploader=channel,
                title=data['snippet']['title'],
                category_id=data['snippet']['categoryId'],
                description=data['snippet']['description'],
                duration=duration.total_seconds(),
                view_count=data['statistics']['viewCount'],
                favorite_count=data['statistics']['favoriteCount'],
                comment_count=data['statistics']['commentCount'],
                uploaded=dateutil.parser.parse(data['snippet']['publishedAt']),
                updated=dateutil.parser.parse(data['snippet']['publishedAt']),
            )
        else:
            video.title = data['snippet']['title']
            video.description = data['snippet']['description']
            video.view_count = data['statistics']['viewCount']
            video.favorite_count = data['statistics']['favoriteCount']
            video.comment_count = data['statistics']['commentCount']
            video.updated = dateutil.parser.parse(
                data['snippet']['publishedAt'])
            video.save()

        return video


class Video(models.Model):
    objects = VideoQuerySet.as_manager()

    youtubeid = models.TextField(unique=True)
    uploader = models.ForeignKey(Channel, related_name='videos')
    title = models.TextField(default='')
    duration = models.IntegerField(default=0)  # in seconds
    category = models.ForeignKey(Category, related_name='videos')
    view_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    uploaded = models.DateTimeField()
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
        return unicode(self.youtubeid)

    def save(self, *args, **kwargs):
        if not self.uploaded:
            self.uploaded = timezone.now()

        if not self.updated:
            self.updated = self.uploaded

        super(Video, self).save(*args, **kwargs)


class Tag(models.Model):
    name = models.TextField(unique=True, verbose_name='Tagname')
    background_color = models.TextField(
        default='#777', verbose_name='Background color')
