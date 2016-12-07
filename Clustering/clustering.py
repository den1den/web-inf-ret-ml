import math
import re

def make_list_of_string(string_list):
    """ Makes a list of a string that is made like a list

    :param string_list: a string written in listchar
    :return: a list of the strings
    """

    new_list = re.sub("\[|\]|,|'", '', string_list)
    return new_list.split(' ')


def find_tweets_with_keywords(tweets, keywords, combination):
    """ Tries to find tweets that have at least one of the keywords in them

    :param tweets: The to be checked tweets
    :param article: The article
    :param combination: The number of keywords that need to be in the tweet to select it
    :return: A list of the ids that are in the article
    """

    article_tweets = []

    for tweet in tweets:
        combi_number = 0
        for keyword in keywords:
            tweet_keywords = make_list_of_string(tweet['keywords'])
            if keyword in tweet_keywords:
                combi_number += 1
            if combi_number == combination:
                article_tweets.append(tweet)
                break

    return article_tweets

def cluster_tweets_by_time(tweets, time):
    """ Clusters the tweets by time

    :param tweets: A list of tweets
    :param time: The time tho cluster the tweets (int)
    :return: A listed list of tweets
    """

    min_time = int(tweets[1]['n_unicode'])
    max_time = int(tweets[1]['n_unicode'])
    for tweet in tweets:
        if int(tweet['n_unicode']) < min_time:
            min_time = int(tweet['n_unicode'])
        elif int(tweet['n_unicode']) > max_time:
            max_time = int(tweet['n_unicode'])

    time_span = max_time - min_time

    clusters = []

    for i in range(math.ceil(time_span / time)):
        clusters.append([])

    for tweet in tweets:
        index = math.floor((int(tweet['n_unicode']) - min_time) / time)
        clusters[index].append(tweet)

    return clusters