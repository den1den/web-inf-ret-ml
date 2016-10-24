import re


def preprocess_tweet(plain_tweet):
    """ Preprocesses a tweets for feature extraction

    :param plain_tweets: tweets in json format
    :return: tweets preprocessed
    """

    return preprocess_text(plain_tweet,'text')


def preprocess_article(plain_article):
    """ Preprocesses the article for feature extraction

    :param plain_article: article details in json format
    :return: article preprocessed
    """

    if hasattr(plain_article, 'Publish date'):
        del plain_article['Publish date']

    return preprocess_text(preprocess_text(plain_article, 'Description'), 'Title')


def give_unique_ids(tweets):
    """ Gives unique ids to the tweets

    :param tweets: a list of tweets
    :return: list of tweets with unique ids
    """

    unique_IDs = set()
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
            unique_IDs.add(new_ID)
        else:
            unique_IDs.add(tweet_ID)

    return tweets

def preprocess_text(item, text='text'):
    """ Preprocess text in items.

    :param item: The item with text that needed preprocessing
    :param text: The text that needs preprocessing
    :return: the item with preprocessed text
    """

    item['real_' + text] = item[text]
    item[text] = strip_text(item[text])
    item['keywords_' + text] = extract_keywords(item[text])

    return item

url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
html_regex = r'<[^<]+?>'
regex1 = re.compile(html_regex)
regex2 = re.compile(url_regex)
regex3 = re.compile(r"[^\w\s]")

def strip_text(raw_text):
    """ Strip the full_text to base

    :param raw_text: raw text
    :return: A stripped full text
    """

    # Remove all non-roman and numeric characters
    return regex3.sub("", regex2.sub("", regex1.sub("", raw_text)))


def extract_keywords(full_text, stop_list = None):
    """
    :param full_text: The full text of a tweet
    :return: The keywords in the tweet
    """

    if stop_list is None:
        # Stop words
        stop_list = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
                     'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'were', 'will', 'with']
        # stop word retweet
        stop_list.append('rt')

    raw_words = set(full_text.split())
    for word in set(raw_words):
        raw_words.remove(word) if word in stop_list else None

    return raw_words