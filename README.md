# Project E4 : Tweets sentiment analyzer

# Getting Started

### Twitter credentials

In this project we scrapped tweets from twitter using twitter API (tweepy).
In order to use twitter API you HAVE to get your own twitter credentials. 
To do so, you have to create a developper account.

You can follow this tutorial : https://rapidapi.com/blog/how-to-use-the-twitter-api/#:~:text=%20How%20to%20Connect%20to%20the%20Twitter%20API,one%20of%20the%20endpoints%20such%20as...%20More

Once you have your credentials, modify twitter_credentials.py 

*Remember never to commit your secrets keys.

### Installation

```shell
$ git clone https://github.com/aitarkom/tweet_analyzer.git
$ cd plotlydash-flask-tutorial
``` 

Run deploy

If deploy fails to run for some reason than please just run wsgi.py
-----

### The project

Once you ran the project, you will get to the home page. At this point click "Go to the project".

The DataTable is initialized with the first 100 tweets taken from Joe Biden's twitter timeline. You can modify this at the line 202 of dashboard.py.
Then, you can chose any word or hashtag you want to analyse tweets sentiments from. You can also change the number of tweets taken at the line 205 of dashboard.py. 
However you cannot take too much tweets at once because twitter will not allow it.

We decided to put every tweet with a polarity higher than 0 as positive, equal 0 as neutral and under 0 as negative.
If you take a closer look to each tweet's polarity, you may notice that sometimes its higher than 0 but you feel like the sentiment of the tweet is more negative than positive
However we noticed that for a big amount of tweets taken, the overall sentiment become more precise. 





