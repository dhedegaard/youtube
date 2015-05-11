import logging

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import Channel

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
                # Fetch data for the channel, updating if needed.
                channel.update_channel_info()
                # Fetch data about videos on the given channel.
                channel.fetch_videos()
                channel.updated = timezone.now()
                channel.save()

        # All done
        logger.info('Done')
