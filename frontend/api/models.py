from django.db import models

from inputoutput.getters import get_tweets_by_date


class TweetCountCache(models.Model):
    count = models.PositiveIntegerField()
    day = models.DateField(primary_key=True)

    @staticmethod
    def get_or_create(day):
        try:
            return TweetCountCache.objects.filter(day=day).get()
        except TweetCountCache.DoesNotExist:
            n = len(get_tweets_by_date(day, day))
            tc = TweetCountCache(count=n, day=day)
            tc.save()
            return tc
