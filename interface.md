# Preprocessing interface

## Tweets

### Data
What should be the output of the preprocessing
- `id:int`: unique id for each tweet
- `keywords`: (For later, too complex for now) all keywords from the `text`, normalized to lowercase, split by spaces, excluding very often used words like 'The'.
- `text:string`: normalized, trimmed, no special characters, no emoticons
- `is_retweet:bool`: `true` iff this tweet is a retweet from some other tweet
    If it is a retweet:
    - 'retweet_id:int': The id of the retweeted tweet
- 'retweet_count:int': How many time is it retweeted
- `urls:int`: the number of external urls that is mentioned in this tweet
- `hashtags_count:int`: the number of hashtags used.
- `hashtags:array[string]`: normalized, unique, space seperated, hashtags that are used
- 'userid:int': the user id of the one posting the tweet

Aside from the data, a separate list of the users with:
- 'userid:int': the id of the user that posted the tweet
- 'friends_count:int': The number of friends of the user
- 'followers_count:int': The number of followers of the user
- 'favourites_count:int': The number of favourites of the user
- 'statuses_count:int': The number of statuses of the user
- `created_at:int`: When the user profile is created (as unix timestamp)
- `location:string`: Location of the user (The state is also enough)


## Constraints
Constraints on the original data
- `lang`: always 'en'
