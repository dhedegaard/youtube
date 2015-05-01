import requests
import dateutil.parser
from django.db import models


class Channel(models.Model):
    author = models.TextField(unique=True)
    title = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', related_name='channels')

    def __unicode__(self):
        return u'id: %s, author: %s' % (
            self.id,
            self.author,
        )

    def update_channel_info(self, save=True):
        resp = requests.get(
            'https://gdata.youtube.com/feeds/api/users/%s'
            '?v=2.1&alt=json' % self.author
        )
        resp.raise_for_status()
        resp = resp.json()
        new_title = resp['entry']['title']['$t']
        if new_title != self.title:
            self.title = new_title
            if save:
                self.save(update_fields=['title'])

    def fetch_videos(self, force=False):
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
                rating=row.get('rating', 0.0),
                like_count=row.get('likeCount', 0),
                rating_count=row.get('ratingCount', 0),
                view_count=row.get('viewCount', 0),
                favorite_count=row.get('favoriteCount', 0),
                comment_count=row.get('commentCount', 0),
                uploaded=dateutil.parser.parse(row['uploaded']),
                updated=dateutil.parser.parse(row['updated']),
            )
        else:
            video.title = row['title']
            video.description = row['description']
            video.rating = row.get('rating', 0.0)
            video.like_count = row.get('likeCount', 0)
            video.rating_count = row.get('ratingCount', 0)
            video.view_count = row.get('viewCount', 0)
            video.favorite_count = row.get('favoriteCount', 0)
            video.comment_count = row.get('commentCount', 0)
            video.updated = dateutil.parser.parse(row['updated'])
            video.save()

        return video


class Video(models.Model):
    objects = VideoQuerySet.as_manager()

    youtubeid = models.TextField(unique=True)
    uploader = models.ForeignKey(Channel, related_name='videos')
    title = models.TextField(default='')
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
    description = models.TextField(default='')

    @property
    def url(self):
        return 'https://www.youtube.com/watch?v=%(youtubeid)s' % {
            'youtubeid': self.youtubeid,
        }

    def __unicode__(self):
        return unicode(self.youtubeid)


class Tag(models.Model):
    name = models.TextField(unique=True, verbose_name=u'Tagname')
    background_color = models.TextField(
        default='#777', verbose_name=u'Background color')
