from __future__ import unicode_literals
import logging
import time

import requests
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import Channel, Video

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-f', '--full', dest='full', action='store_true',
                            help='Do full fetch on all channels.')

    def handle(self, *args, **options):
        logger.info('Starting')

        # Check to see if we should do a full fetch or not.
        full_fetch = options.get('full', False)
        if full_fetch:
            logger.warning('Doing full fetch on all channels, this might take '
                           'a long time.')

        # Fetch the channels.
        channels = Channel.objects.all()
        channel_len = len(channels)

        if channel_len == 0:
            logger.warning('There are no channels to update.')
            return

        # Iterate on each channel, fetching data as we go along.
        for idx, channel in enumerate(channels):
            logger.info('  [%s/%s] fetching for channel: %s',
                        idx + 1, channel_len, channel.author)
            with transaction.atomic():
                for attempt in range(5):
                    try:
                        # Fetch data for the channel, updating if needed.
                        channel.update_channel_info()
                        # Fetch data about videos on the given channel.
                        fetched = channel.fetch_videos(full_fetch=full_fetch)
                        channel.updated = timezone.now()
                        channel.save()
                    except requests.exceptions.RequestException as e:  # pragma: nocover  # NOQA
                        # If we're at the last attempt, raise.
                        if attempt == 4:
                            raise

                        # Otherwise try again until 5 attempts have been made.
                        logger.warning(
                            'Got exception trying to fetch youtube data')
                        logger.exception(e)
                        try:
                            logger.error('Body: %s', e.response.text)
                        except AttributeError:
                            logger.error('Body: <no request found>')
                        # Wait for a second before trying again.
                        time.sleep(5)
                    else:
                        # No exception, proceed with next channel.
                        break
            logger.info('    fetched %s videos', fetched)

        # Iterate on the last 500 videos, checking HEAD state of thumbnail.
        logger.info('Marking deleted videos as deleted')
        for video in Video.objects.exclude_deleted().order_by('-id')[:500]:
            with transaction.atomic():
                # Do HTTP HEAD request, to fetch status code without body.
                resp = requests.head(video.get_thumbnail())

                if resp.status_code == 200:
                    # The video is still accessible.
                    continue
                elif resp.status_code == 404:
                    # The video has been deleted, mark it as such.
                    video.deleted = True
                    video.save()
                    logger.info('  Marking %s as deleted', video.youtubeid)
                else:
                    # WTF, let's see what happens.
                    resp.raise_for_status()

        # All done
        logger.info('Done')
