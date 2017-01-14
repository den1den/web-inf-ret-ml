from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, StringRelatedField

from frontend.api.models import TweetCountCache, Tweet, Article, TweetClusterMembership, Cluster, \
    TweetClusterAttributeValue


class TweetCountCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetCountCache
        fields = ('count', 'day',)


# class TweetSerializer(serializers.ModelSerializer):
#     id = serializers.SerializerMethodField('get_tweet_id')
#
#     class Meta:
#         model = Tweet
#         fields = ('id',)
#
#     def get_tweet_id(self, tweet):
#         return str(tweet)


# class ArticleSerializer(serializers.ModelSerializer):
#     id = serializers.SerializerMethodField('get_article_id')
#
#     class Meta:
#         model = Article
#         fields = ('id',)
#
#     def get_article_id(self, article):
#         return str(article)


# class AttributeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TweetClusterAttributes
#         fields = ('name', )


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = TweetClusterAttributeValue
        fields = ('attribute', 'value')


class TweetClusterMembershipSerializer(serializers.ModelSerializer):
    tweet = StringRelatedField()
    attributes = AttributeValueSerializer(source='tweetclusterattributevalue_set', many=True)

    class Meta:
        model = TweetClusterMembership
        fields = ('tweet', 'attributes')


class ClusterSerializer(serializers.ModelSerializer):
    tweets = TweetClusterMembershipSerializer(source='tweetclustermembership_set', many=True)
    article = StringRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='cluster-detail')

    class Meta:
        model = Cluster
        fields = ('id', 'tweets', 'article', 'url', 'rumor_ration', )
