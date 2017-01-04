from rest_framework import serializers

from frontend.api.models import TweetCountCache, TweetCluster, Tweet


class TweetCountCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetCountCache
        fields = ('count', 'day',)
