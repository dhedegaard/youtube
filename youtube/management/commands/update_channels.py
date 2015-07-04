import logging
import time

import requests
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import Channel, Video

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info('Starting')

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
                for attempt in xrange(5):
                    try:
                        # Fetch data for the channel, updating if needed.
                        channel.update_channel_info()
                        # Fetch data about videos on the given channel.
                        channel.fetch_videos()
                        channel.updated = timezone.now()
                        channel.save()
                    except requests.exceptions.RequestException, e:  # pragma: nocover  # NOQA
                        # If we're at the last attempt, raise.
                        if attempt == 4:
                            raise

                        # Otherwise try again until 5 attempts have been made.
                        logger.warning(
                            'Got exception trying to fetch youtube data')
                        logger.exception(e)
                        # Wait for a second before trying again.
                        time.sleep(1)
                    else:
                        # No exception, proceed with next channel.
                        break

        # Iterate on all videos, checking HEAD state of thumbnail.
        logger.info('Marking deleted videos as deleted')
        for video in Video.objects.exclude_deleted():
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
