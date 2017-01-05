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


class Tweet(models.Model):
    def get_tweet_id(self):
        return 't' + self.id


class Article(models.Model):
    def get_article_id(self):
        return 'r' + self.id


class TweetCluster(models.Model):
    article = models.ForeignKey(Article)
    tweets = models.ManyToManyField(Tweet)
