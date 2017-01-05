from rest_framework import serializers

from frontend.api.models import TweetCountCache, TweetCluster, Tweet, Article


class TweetCountCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetCountCache
        fields = ('count', 'day',)


class TweetSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_tweet_id')

    class Meta:
        model = Tweet
        fields = ()


class ArticleSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_article_id')

    class Meta:
        model = Article
        fields = ()


class TweetClusterSerializer(serializers.ModelSerializer):
    tweets = TweetSerializer(many=True)
    article = ArticleSerializer()

    class Meta:
        model = TweetCluster
        fields = ('tweets', 'article', )
