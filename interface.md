# Preprocessing interface

## Tweets

### Data
What should be the output of the preprocessing
- `id:int`: unique id for each tweet
- `keywords`: (For later, to complex for now) all keywords from the `text`, normalized to lowercase, split by spaces, excluding very often used words like 'The'.
- `text:string`: normalized, trimmed, no special characters, no emoticons
- `is_retweet:bool`: `true` iff this tweet is retweet from some other tweet
- `urls:int`: the number of external urls that is mentioned in this tweet
- `hashtags_count:int`: the number of hashtags used.
- `hashtags:array[string]`: normalized, unique, space seperated, hashtags that are used

## Constraints
Constraints on the original data
- `lang`: always 'en'
