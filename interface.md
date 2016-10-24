# Preprocessing interface
This describes the interface between the machine learning and preprocessing.
If you have any questions please do not hestitate to use whatsapp and make changes to this document.
Ideally the preprocessing step is ran directly after the data retrieval step such that the retrieved data is only written to disk AFTER it is preprocessed. Please discuss this with Adrian.

## Normalization on strings
We will ask for multiple types of normalization. These are described below:
- RAW: no normalization applied, just copied text
- NORM1: Decapitalized text + No punctuation like `,.#@(){}[]` and so on + No HTML
- NORM2: NORM1 + removal of Stop words + removal of retweet (`RT` or `rt` at start of tweet)
- NORM3: Most stripped form, inclusing NORM1 + NORM2 + Tokenization + multiple techniques as described in http://nlp.stanford.edu/IR-book/html/htmledition/the-term-vocabulary-and-postings-lists-1.html. TODO: please define this properly so we know what to expect.

## Unix timestamp
Can be int or long. See http://stackoverflow.com/questions/732034/getting-unixtime-in-java for a java implementation.

# 1. RSS / Articles

### Article data
Output of the preprocessing from the articles, written to a seperate json file
- `id:int`: unique id for each article
- `description:string`: A discription of the article (RAW for now)
- `published_date:int`: When the article was published (as a unix timestamp)
- `title:string`: Title of the article (RAW)
- `author_id:set(int)`: A set of unique ids for the authors of this article
- `link:url`: link to the page where this article is shown

### Article author data
Output of the preprocessing from the article authors, written to a seperate json file
- `author_id:int`: Article id like in the Article data
- `name:string`: The name of the author (RAW)

### Constraints
None for now

# 2. Tweets

### Tweet data
Output of the preprocessing from the tweets, written to a seperate json file
- `id:int`: unique id for each tweet
- `text_1:string`: the full text of the tweet (thus not ending with ...). (NORM1 if possible, otherwise RAW)
- `text_2:string`: all keywords from the tweet text split by spaces. (NORM2 if possible, otherwise RAW)
- `is_retweet:bool`: `true` iff this tweet is a retweet from some other tweet `false` otherwise
- `retweet_count:int`: How many time this tweet has been retweeted
- `urls:int`: the number of external urls that is mentioned in this tweet
- `hashtags:array[string]`: the hashtags that were used in this tweet (RAW)
- `hashtags_normal:array[string]`: the hashtags that were used in this tweet (NORM1 if possible with the exception that we want to split words that were in CamelCase or SNAKE_CASE)
- `user_id:int`: the user id of the user that posted this tweet

### Tweet user data
Output of the preprocessing from the tweet users, written to a seperate json file
- `user_id:int`: the id of the user that posted a tweet
- `friends_count:int`: The number of friends of the user
- `followers_count:int`: The number of followers of the user
- `favourites_count:int`: The number of favourites of the user
- `statuses_count:int`: The number of statuses of the user
- `created_at:int`: When the user profile is created (as unix timestamp)
- `location:string`: Location of the user (the state is also enough, RAW)

### Constraints
Constraints on the original data
- `lang`: always 'en'
