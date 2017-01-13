import json
import os

from django.core.management.base import BaseCommand, CommandError

from frontend.api.models import TweetCluster, Article, Tweet


class Command(BaseCommand):
    help = 'Load in a cluster file'

    def add_arguments(self, parser):
        parser.add_argument('--cluster_file')

    def handle(self, *args, **options):
        if not os.path.exists(options['cluster_file']):
            raise CommandError('cluster_file "%s" does not exist' % options['cluster_file'])

        clusters = json.load(open(options['cluster_file']))
        created = 0
        for article_id, cluster_dict in clusters.items():
            if not 'r' == article_id[0]:
                self.stdout.write(self.style.WARNING('Could not import article with non article id: %s' % article_id))
                continue
            article, c = Article.objects.get_or_create(id=int(article_id[1:]))
            if c:
                created += 1

            tweets = []
            print(cluster_dict['tweets'])
            for tweet_id in cluster_dict['tweets']:
                # tweet_id is int, no string. So: assert 't' == tweet_id[0]
                assert type(tweet_id) is int
                tweet, c = Tweet.objects.get_or_create(id=tweet_id)
                if c:
                    created += 1
                tweets.append(tweet)

            if len(tweets) == 0:
                continue

            missing = False
            for tweet in tweets:
                if not TweetCluster.objects.filter(article=article.pk, tweets__exact=tweet.id).exists():
                    missing = True
                    break
            if missing:
                tc = TweetCluster(article=article)
                tc.save()
                tc.tweets.add(*tweets)
                created += 1

        self.stdout.write(self.style.SUCCESS('Successfully imported clusters, created %d entries' % created))
