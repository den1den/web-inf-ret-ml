import re

def preprocess_tweet(plain_tweets):
    """ Preprocesses the tweets for feature extraction

    :param plain_tweets: tweets in json format
    :return: tweets preprocessed
    """

    for tweet in plain_tweets:
        tweet['text'] = strip_text(tweet['text'])
        tweet['keywords'] = extract_keywords(tweet['text'])

    return plain_tweets


def give_unique_ids(tweets):
    """ Gives unique ids to the tweets

    :param tweets: a list of tweets
    :return: list of tweets with unique ids
    """

    unique_IDs = []
    new_ID = 1

    # Makes the tweet ID's positive and checks whether the ID already exists.
    for tweet in tweets:

        # Positive id
        tweet.id = abs(tweet.id)

        # If tweet ID already exists, give new ID. Otherwise, keep ID
        tweet_ID = tweet.id
        if tweet_ID in unique_IDs:
            while new_ID in unique_IDs:
                new_ID += 1
            tweet.id = new_ID
            unique_IDs.append(new_ID)
        else:
            unique_IDs.append(tweet_ID)

    return tweets


def strip_text(full_text):
    """ Strip the full_text to base

    :param full_text:
    :return: A stripped full text
    """

    return re.sub("[^\w]", " ", full_text)

def extract_keywords(full_text):
    """

    :param full_text: The full text of a tweet
    :return: The keywords in the tweet
    """
    return re.sub("[^\w]", " ", full_text).split()
