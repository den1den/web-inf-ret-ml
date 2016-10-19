# import preprocessing.rake as pr
from extract_tweets.models import Tweet


def preprocess_tweet(plain_tweets):
    """ Preprocesses the tweets for feature extraction

    :param plain_tweets: tweets in json format
    :return: tweets preprocessed
    """

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

def extract_words(full_text):
    """

    :param full_text: The full text of a tweet
    :return: The keywords in the tweet
    """

    keywords = pr.Rake(full_text, 3, 5, 1)

    return keywords