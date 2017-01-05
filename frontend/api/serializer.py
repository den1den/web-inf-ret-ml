from rest_framework import serializers

from frontend.api.models import TweetCountCache, TweetCluster, Tweet, Article


class TweetCountCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetCountCache
        fields = ('count', 'day',)


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ('id', )


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', )


class TweetClusterSerializer(serializers.ModelSerializer):
    tweets = TweetSerializer(many=True)
    article = ArticleSerializer()

    class Meta:
        model = TweetCluster
        fields = ('tweets', 'article', )
