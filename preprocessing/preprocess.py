import re

def preprocess_tweet(plain_tweets):
    """ Preprocesses the tweets for feature extraction

    :param plain_tweets: tweets in json format
    :return: tweets preprocessed
    """

    for tweet in plain_tweets:
        print(tweet)
        tweet['real_text'] = tweet['text']
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

url_regex = r'~(?:\b[a-z\d.-]+://[^<>\s]+|\b(?:(?:(?:[^\s!@#$%^&*()_=+[\]{}\|;:\'",.<>/?]+)\.)+(?:ac|ad|aero|ae|af|ag|ai|al|am|an|ao|aq|arpa|ar|asia|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|biz|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|cat|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|coop|com|co|cr|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|edu|ee|eg|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gov|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|info|int|in|io|iq|ir|is|it|je|jm|jobs|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mil|mk|ml|mm|mn|mobi|mo|mp|mq|mr|ms|mt|museum|mu|mv|mw|mx|my|mz|name|na|nc|net|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|org|pa|pe|pf|pg|ph|pk|pl|pm|pn|pro|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|tc|td|tel|tf|tg|th|tj|tk|tl|tm|tn|to|tp|travel|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|xn--0zwm56d|xn--11b5bs3a9aj6g|xn--80akhbyknj4f|xn--9t4b11yi5a|xn--deba0ad|xn--g6w251d|xn--hgbk6aj7f53bba|xn--hlcj6aya9esc7a|xn--jxalpdlp|xn--kgbechtv|xn--zckzah|ye|yt|yu|za|zm|zw)|(?:(?:[0-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:[0-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5]))(?:[;/][^#?<>\s]*)?(?:\?[^#<>\s]*)?(?:#[^<>\s]*)?(?!\w))~iS'
url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
regex1 = re.compile(url_regex)
regex2 = re.compile(r"[^\w\s]")

def strip_text(raw_text):
    """ Strip the full_text to base

    :param raw_text: raw text
    :return: A stripped full text
    """

    # Remove all non-roman and numeric characters
    return regex2.sub("", regex1.sub("", raw_text))


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

    raw_words = full_text.split()
    for word in raw_words:
        raw_words.remove(word) if word in stop_list else None

    return raw_words
