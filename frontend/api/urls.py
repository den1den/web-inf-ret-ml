from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from frontend.api.views import TweetCountCacheViewSet, get_tweet_counts_week, TweetClusterViewSet

router = DefaultRouter()
router.register(r'tweet_count_cache', TweetCountCacheViewSet)
router.register(r'tweet_cluster', TweetClusterViewSet)
urlpatterns = router.urls + [
    url(r'tweet_count_week', get_tweet_counts_week)
]
