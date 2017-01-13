import json
import os

from django.core.management.base import BaseCommand, CommandError

from frontend.api.models import Article, Tweet, TweetClusterMembership, Cluster, TweetClusterAttributes, \
    TweetClusterAttributeValue


class Command(BaseCommand):
    help = 'Load in a cluster file'

    def add_arguments(self, parser):
        parser.add_argument('--cluster_file')
        parser.add_argument('--rebuild', action='store_true')

    def handle(self, *args, **options):
        if not os.path.exists(options['cluster_file']):
            raise CommandError('cluster_file "%s" does not exist' % options['cluster_file'])

        if options['rebuild']:
            Cluster.objects.all().delete()
            TweetClusterAttributes.objects.all().delete()

        clusters = json.load(open(options['cluster_file']))
        created = 0
        for article_id, cluster_dict in clusters.items():
            # match article
            if not 'r' == article_id[0]:
                self.stdout.write(self.style.WARNING('Could not import article with non article id: %s' % article_id))
                continue
            article, c = Article.objects.get_or_create(id=int(article_id[1:]))
            if c:
                created += 1

            # match tweets
            tweets = []
            for tweet_dict in cluster_dict['tweets']:
                assert type(tweet_dict['id']) is str
                assert tweet_dict['id'][0] == 't'
                tweet_id = int(tweet_dict['id'][1:])
                tweet, c = Tweet.objects.get_or_create(id=tweet_id)
                if c:
                    created += 1
                tweets.append(tweet)

            if len(tweets) == 0:
                continue

            # find clusters with ALL these tweets
            cluster_candidates = [m.cluster for m in TweetClusterMembership.objects.filter(tweet=tweets[0]).all()]
            for tweet in tweets[1:]:

                cc_of_next_tweet = [m.cluster for m in TweetClusterMembership.objects.filter(tweet=tweet).all()]

                for cluster in tuple(cluster_candidates):
                    if cluster not in cc_of_next_tweet:
                        cluster_candidates.remove(cluster)

                if len(cluster_candidates) == 0:
                    break


            # remove clusters with more
            for c in cluster_candidates:
                if len(c.tweets.all()) != len(tweets):
                    cluster_candidates.remove(c)

            # process
            if len(cluster_candidates) == 1:
                # One found
                cluster = cluster_candidates[0]

                self.stdout.write(self.style.NOTICE('Updating: %s' % cluster_dict['tweets']))
                i = 0
                for tweet_dict in cluster_dict['tweets']:
                    tweet = tweets[i]
                    m = TweetClusterMembership.objects.get(tweet=tweet, cluster=cluster)

                    # ADD values: warning does not update but just adds the values
                    attribut_values = []
                    for key, value in tweet_dict.items():
                        if key == 'id':
                            continue
                        attribute, c = TweetClusterAttributes.objects.get_or_create(name=key)
                        if c:
                            created += 1

                        attribute_value = None
                        try:
                            attribute_value = TweetClusterAttributeValue.objects.filter(tweet_cluster_membership=m, attribute=attribute).first()
                            if attribute_value is None:
                                TweetClusterAttributeValue.objects.create(tweet_cluster_membership=m, attribute=attribute, value=value)
                                created += 1
                            else:
                                # update
                                attribute_value.value = value
                                attribute_value.save()
                        except Exception as e:
                            self.stdout.write(self.style.ERROR('Could not update attribute value %s in %s (%s)' % (key, tweet_dict, attribute_value)))


                    m.attributes.add(*attribut_values)
            elif len(cluster_candidates) == 0:
                # None found

                self.stdout.write(self.style.NOTICE('  Adding: %s' % cluster_dict['tweets']))
                # create cluster
                cluster = Cluster.objects.create(article=article)
                cluster.save()
                created += 1

                # add tweet memberships
                i = 0
                for tweet_dict in cluster_dict['tweets']:
                    tweet = tweets[i]
                    m = TweetClusterMembership.objects.create(tweet=tweet, cluster=cluster)
                    m.save()
                    i += 1

                    # update values
                    for key, value in tweet_dict.items():
                        if key == 'id':
                            continue
                        attribute, c = TweetClusterAttributes.objects.get_or_create(name=key)
                        if c:
                            created += 1
                        try:
                            attribute_value = TweetClusterAttributeValue.objects.create(tweet_cluster_membership=m, attribute=attribute, value=value)
                            created += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR('Could not store attribute %s in %s' % (key, tweet_dict)))
            else:
                self.stdout.write(self.style.ERROR('Many clusters found. tweets = %s, clusters = %s' % (tweets, cluster_candidates)))
            # if missing:
            #     tc = TweetCluster(article=article)
            #     tc.save()
            #     tc.tweets.add(*tweets)
            #     created += 1

        self.stdout.write(self.style.SUCCESS('Successfully imported clusters, created %d entries' % created))
