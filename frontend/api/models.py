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
    def __str__(self):
        return self.get_tweet_id()

    def get_tweet_id(self):
        return 't%d' % self.id


class Article(models.Model):
    def __str__(self):
        return self.get_article_id()

    def get_article_id(self):
        return 'r%d' % self.id


class TweetClusterAttributes(models.Model):
    name = models.CharField(max_length=128)


class TweetClusterAttributeValue(models.Model):
    attr = models.ForeignKey(TweetClusterAttributes)
    val = models.DecimalField(max_digits=4 + 6, decimal_places=6)


class Cluster(models.Model):
    article = models.ForeignKey(Article)
    tweets = models.ManyToManyField(Tweet, through='TweetClusterMembership')
    checked = models.BooleanField(default=False)


class TweetClusterMembership(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    attributes = models.ManyToManyField(TweetClusterAttributeValue)
