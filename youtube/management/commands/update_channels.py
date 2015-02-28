import logging

from django.core.management import BaseCommand
from django.db import transaction

from ...models import Channel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info('Starting')
        for channel in Channel.objects.all():
            logger.info('  fetching for channel: %s', channel.author)
            with transaction.atomic():
                channel.fetch()
        logger.info('Done')
