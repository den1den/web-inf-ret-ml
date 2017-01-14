import itertools
import subprocess
from datetime import timedelta

import django_filters
from django.http.response import StreamingHttpResponse, JsonResponse
from django.utils.html import escape
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from config.config import PHP_MAIN_SCRIPT
from frontend.api.models import TweetCountCache, Cluster
from frontend.api.serializer import TweetCountCacheSerializer, ClusterSerializer
from frontend.base.pagination import LimitedPagenumbrPagination


def stream_command_output_git():
    return itertools.chain(stream_command_output('git pull'), '---', stream_command_output('git status'))


def stream_command_output(command):
    yield "<pre>"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        out = process.stdout.read(1024).decode("utf-8")
        if out == '' and process.poll() is not None:
            break
        if out != '':
            yield escape(out)
    yield "</pre>"


class TestPhpOutputView(View):
    def get(self, request, *args, **kwargs):
        php_args = 'test_command'
        return StreamingHttpResponse(stream_command_output(PHP_MAIN_SCRIPT + ' ' + php_args))


# Tweet Counts ################################################################
class TweetCountCacheViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ### Get the tweet count per date.
    If jQuery is used the array should be passed after `$.ajaxSettings.traditional = true;`

    The endpoint of tweet counts per week is in GET [tweet_count_week](/tweet_count_week)
    You do have to supply start and end parameters formatted as "YEAR weeknumber", such as: [tweet_count_week/?start=2016 1&end=2016 3](/tweet_count_week/?start=2016%201&end=2016%203)
    """
    serializer_class = TweetCountCacheSerializer
    queryset = TweetCountCache.objects.all()


class TweetCountWeeksValidator(Serializer):
    start = serializers.DateField(input_formats=['%Y %W %w'])  # DateField
    end = serializers.DateField(input_formats=['%Y %W %w'])  # DateField


@api_view(['GET'])
def get_tweet_counts_week(request: Request):
    data = request.query_params.copy()
    if not data['start'].endswith(' 0'):
        data['start'] += ' 0'
    if not data['end'].endswith(' 0'):
        data['end'] += ' 0'
    v = TweetCountWeeksValidator(data=data)
    v.is_valid(raise_exception=True)
    start = v.validated_data['start']
    end = v.validated_data['end']

    result = {}

    week_start = start
    while week_start <= end:
        result_key = week_start.strftime('%Y %W')

        n = 0
        d = week_start
        next_week_start = week_start + timedelta(weeks=1)
        while d < next_week_start:
            tc = TweetCountCache.get_or_create(day=d)
            n += tc.count

            d += timedelta(days=1)

        result[result_key] = n

        week_start = next_week_start

    return JsonResponse(result)


# Tweet Clusters ################################################################
class ArticleFilter(django_filters.rest_framework.FilterSet):
    article = django_filters.CharFilter(name="article__article_id")

    class Meta:
        model = Cluster
        fields = ['article']

class ClusterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    These are all the clusters that we have
    """
    serializer_class = ClusterSerializer
    # queryset = Cluster.objects.filter(article__article_id='r405155958')
    queryset = Cluster.objects.all()
    pagination_class = LimitedPagenumbrPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ArticleFilter


class ClusterManualViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get all tweet clusters that have not yet been manually rated
    """
    serializer_class = ClusterSerializer
    queryset = Cluster.objects.filter()
    pagination_class = LimitedPagenumbrPagination
