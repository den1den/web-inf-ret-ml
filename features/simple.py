from extract_tweets.models import Tweet


def scan_conversations_start(tweets):
    return scan_conversations({}, 0, tweets)


def scan_conversations(conversation_mapping, n_conversations, tweets):
    """Scans tweets and ranks them based on the retweets.
    -conversation_mapping: Mapping such that conversation_mapping[tweet_id] == tweet_conversation
    -n_n_conversations: The next index for a newly found conversation
    -tweets: The tweets to add to the conversation_mapping
    """
    for tweet in tweets:
        assert isinstance(tweet, Tweet)
        source_id = tweet.get_retweet_id()
        if source_id is None:
            # Do not add tweets that are not retweeted
            continue
        if source_id in conversation_mapping:
            conversation_mapping[tweet.id] = conversation_mapping[source_id]
        else:
            conversation_mapping[tweet.id] = n_conversations
            n_conversations += 1
    return conversation_mapping, n_conversations