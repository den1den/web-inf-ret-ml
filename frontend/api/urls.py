from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from frontend.api.views import TweetCountCacheViewSet, get_tweet_counts_week

router = DefaultRouter()
router.register(r'tweet_count_cache', TweetCountCacheViewSet)
urlpatterns = router.urls + [
    url(r'tweet_count_week', get_tweet_counts_week)
]
