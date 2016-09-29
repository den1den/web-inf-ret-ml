# Preprocessing interface

## Tweets

### Data
What should be the output of the preprocessing
- `id`: unique id for each tweet
- `keywords`: all keywords from the `text`, normalized to lowercase, split by spaces, excluding very often used words like 'The'.
- `text`: normalized, trimmed, no special characters, no emoticons
- `is_retweet`: `true` iff this tweet is retweet from some other tweet
- `urls`: the number of external urls that is mentioned in this tweet
- `hashtags_count`: the number of hashtags used.
- `hashtags`: normalized, unique, space seperated, hashtags that are used

## Constraints
Constraints on the original data
- `lang`: always 'en'
