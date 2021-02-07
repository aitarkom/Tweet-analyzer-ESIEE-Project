import tweepy
from tweepy import API
from tweepy import OAuthHandler
from tweepy import Cursor
import re
from textblob import TextBlob
#from wordcloud import WordCloud
import matplotlib.pyplot as plt

import twitter_credentials
import numpy as np
import pandas as pd

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth,  wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweets):
        tweets = re.sub(r'@[A-Za-z0-9]+','',tweets) #supprime les mentions
        tweets = re.sub(r'#','', tweets) # Supprime le symbole '#'
        tweets = re.sub(r'RT[\s]+', '', tweets) # supprime "RT"
        tweets = re.sub(r'https?:\/\/\S+' ,'', tweets) #supprime les liens 

        return tweets

    def getsubjectivity(self,tweets):
        return TextBlob(tweets).sentiment.subjectivity

    def getpolarity(self, tweets):
        return TextBlob(tweets).sentiment.polarity

    # def plotwordcloud(self,df):
    #     words = " ".join([tweet for tweet in  df['cleaned_tweets']])
    #     wordCloud = WordCloud(width = 500, height = 300, random_state= 21, max_font_size=119).generate(words)

    #     plt.imshow(wordCloud, interpolation = "bilinear")
    #     plt.axis('off')
    #     #plt.show()

    def getanalysis(self, score):
        if score < 0 :
            return 'Negative'
        elif score == 0 :
            return 'Neutral'
        else : return 'Positive'

    def getpositivetweets(self,df):
        positivetweet=[]
        j=1
        sortedDF=df.sort_values(by=['polarity'])
        for i in range(0, sortedDF.shape[0]):
            if(sortedDF['Analysis'][i]=='Positive'):
                positivetweet.append(str(j)+')'+sortedDF['Tweets'][i])
                #print(str(j)+')'+sortedDF['Tweets'][i])
                #print()
                j+=1
        return positivetweet

    def getnegativetweets(self,df):
        j=1
        sortedDF=df.sort_values(by=['polarity'], ascending = "False")
        for i in range(0, sortedDF.shape[0]):
            if(sortedDF['Analysis'][i]=='Negative'):
                print(str(j)+')'+sortedDF['Tweets'][i])
                print()
                j+=1

    def gethastagtweets(self,container, n):
        tweets = []
        for tweet in tweepy.Cursor(api.search, q=container).items(n):
            tweets.append(tweet)
        return tweets

    def plotpolsub(self,df):
        plt.figure(figsize=(8,6))
        for i in range (0,df.shape[0]):
            plt.scatter(df['polarity'][i], df['subjectivity'][i], color='Blue')

        plt.title('Sentiment analysis')
        plt.xlabel('Polarity')
        plt.ylabel('Subjectivity')
        plt.show()

    def plotvaluecounts(self,df):
        df["Analysis"].value_counts()

        plt.title('Sentiment Analysis')
        plt.xlabel("Sentiment")
        plt.ylabel('Counts')
        df['Analysis'].value_counts().plot(kind='bar')
        plt.show()

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['geo'] = np.array([tweet.geo for tweet in tweets])
        df['coordinates'] = np.array([tweet.coordinates for tweet in tweets])
        df['place'] = np.array([tweet.place for tweet in tweets])
        df['cleaned_tweets'] = np.array([tweet_analyzer.clean_tweet(tweet) for tweet in df['Tweets']])
        df['subjectivity'] = np.array([tweet_analyzer.getsubjectivity(tweet) for tweet in df['cleaned_tweets']])
        df['polarity'] = np.array([tweet_analyzer.getpolarity(tweet) for tweet in df['cleaned_tweets']])
        df['Analysis'] = np.array([tweet_analyzer.getanalysis(tweet) for tweet in df['polarity']])

        return df


########################################################## CREATING DASHBOARD ######################################################


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from collections import OrderedDict

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

twitter_client = TwitterClient()
tweet_analyzer = TweetAnalyzer()
api = twitter_client.get_twitter_client_api()

def init_dashboard(server):

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dashapp/",
        external_stylesheets=[
            "/static/dist/css/styles.css",
            "https://fonts.googleapis.com/css?family=Lato",
        ],
    )
    
    dash_app.layout = html.Div(
        [
            html.H1("Tweet Analyzer", style={'text-align':'center'}),
            html.Br(),
            dcc.Input(id="selected_hashtag", type="text", placeholder="", debounce=True),
            html.Div(id="container"),
            html.Br(),
            html.Br(),
            dash_table.DataTable(id= "table",
            style_data = {'whiteSpace' : 'normal', 'height' :'auto'},
            style_table={'overflowX': 'scroll','maxHeight' : '350px', 'overflowY' : 'scroll'},
            sort_action="native",
            sort_mode="native",
            fixed_rows={ 'headers': True, 'data': 0 },
            style_cell={'width': '200px'}),
            html.Br(),
            html.H2(id='overall', style={'text-align':'center'}),
            dcc.Graph(id = "plotpolsub_", figure = {}),
            html.Br(),
            dcc.Graph(id = "sentiments", figure = {}),
            html.Br()
        ]
    )


    @dash_app.callback(
        [
        Output(component_id="table",component_property="data"),
        Output(component_id="table", component_property="columns"),
        Output(component_id="container", component_property= "children"),
        Output(component_id="plotpolsub_", component_property="figure"),
        Output(component_id="sentiments", component_property="figure"),
        Output(component_id="overall", component_property="children"),
        ],
        [Input(component_id="selected_hashtag",component_property= "value")]
    )

    def update_output(selected_hashtag):

        container = u'Chosen Hashtag / Word : {}'.format(selected_hashtag)

        if selected_hashtag == None :
            tweets = api.user_timeline(screen_name="HillaryClinton", count=100)
        else : 
            hashtag = str(selected_hashtag)
            tweets = tweet_analyzer.gethastagtweets(hashtag,10)

        df = tweet_analyzer.tweets_to_data_frame(tweets)
        #print(df.head(10))

        mean_pol = df["polarity"].mean()
        overall_pol = ''

        if mean_pol < 0 :
            overall_pol = 'The overall sentiment is Negative'
        elif mean_pol == 0 :
            overall_pol = 'The overall sentiment is Neutral'
        else : overall_pol =  'The overall sentiment is Positive'

        fig1 = px.scatter(df, x="polarity", y='subjectivity', title="tweets polarity")

        df2 = pd.DataFrame(df["Analysis"].value_counts().reset_index().values, columns = ['Sentiments', 'Counts'])

        fig2 = px.bar(df2, x="Sentiments", y="Counts", barmode="group", title= "Sentiment count")

        columns = [{'id': col, 'name': col} for col in df.columns]
        data = df.to_dict(orient="records")

        return  data, columns, container, fig1, fig2, overall_pol
    
    return dash_app.server

