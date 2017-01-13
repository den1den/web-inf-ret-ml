import datetime
import json
import os

from django.core.management.base import BaseCommand

from frontend.api.models import TweetCountCache


class Command(BaseCommand):
    help = 'Load all tweet counts'

    def handle(self, *args, **options):
        start = datetime.datetime(2016, 1, 1)
        end = datetime.datetime(2017, 1, 1)

        n = 0
        d = start
        while d < end:
            tc = TweetCountCache.get_or_create(day=d)
            n += tc.count
            d += datetime.timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully imported clusters, created %d entries' % n))
