# -*- coding:utf-8 -*-

# @Time    : 2022-09-15
# @Author  : Gene Moo Lee, Jaecheol Park and Xiaoke Zhang
# Disclaimer: Students, please do not redistribute this code outside the class. Thank you!


# Note: These are two wrapper classes for Twitter Collection. You are not required to understand the details in this file.
# Please go to `tweet_collection_example.ipynb` to learn how to use this for tweet collections.


import json, time, os
from datetime import datetime

import tweepy
from tweepy import StreamingClient, StreamRule


class TwitterStreamer(StreamingClient):

    def __init__(self, bearer_token):

        # initiate the StreamingClient
        super().__init__(bearer_token = bearer_token)
        
        # whether to show process
        self.show_process = True
        # store the tracked tweets
        self.tweets = []
        # number of tweets to collect
        self.tweet_num = 100
        # query
        self.query = ''
        # file save information
        self.save_result = True
        self.save_dir = ''
        # store result 
        self.result = {}
    
    def on_tweet(self, tweet): 
        '''Overwrite the original function to store all returned tweets
        show_process: If true, print the current tweet collected
        '''
        self.tweets.append(tweet.data)

        # print the current tweet if specified
        if self.show_process:
            print("Tweet No."+ str(len(self.tweets)), tweet.text)

        # check if we have collected enough tweets, if so disconnect
        if len(self.tweets) == self.tweet_num:
            self.result = {}
            self.result['collection_type'] = 'streaming'
            self.result['collection_timestamp'] = time.time()
            self.result['query'] = self.query
            self.result['tweet_cnt'] = len(self.tweets)
            self.result['tweets'] = self.tweets

            if self.save_result:
                with open(self.save_file, 'w', encoding = 'utf-8') as w:
                    w.write(json.dumps(self.result, indent=4))

            self.disconnect()
        
    def clear_rule(self):
        '''Clear the existing rules'''
        rules = self.get_rules().data
        if rules:
            for rule in rules:
                self.delete_rules(rule.id)

    def collect_tweets_stream(self, query
                            , tweets_cnt = 100
                            , show_process = True
                            , save_result = True
                            , save_dir = None 
                            , file_name = None
                            ):
        '''Collecing the tweets from stream. 
        `query`: the search rules. For more information, please see: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md
        `tweet_cnt`: the number of tweets to be collected.
        `show_process`: If true, print the current tweet collected.
        `save_result`: If True, the result will be saved in a json file in the same directory
        `save_dir`: The directory you want to save this file. If not specified, the file will be written in the same directory.
        `file_name`: The file name. If not specified, the file will be named after your searh query and tweet count.
        '''
        try:
            # clear all existing rules
            self.clear_rule()

            # clear the existing data
            self.tweets = []

            # set the number of tweets to collect
            self.tweet_num = tweets_cnt

            # set whether to show process and whether to save_result
            self.show_process = show_process
            self.save_result = save_result

            # specify directory 
            if not file_name:  # file name not specified
                file_name = 'streaming' + query.replace(':','-')+'_'+str(self.tweet_num)+'.json'
            if save_dir:
                if not os.path.exists(save_dir):  # make sure the direcroty exists
                    os.makedirs(save_dir)
                self.save_file = os.path.join(save_dir, file_name)
            else:
                self.save_file = file_name
                
            
            # add rules
            self.query = query
            rule = StreamRule(value = query)
            self.add_rules(rule)

            # start running

            # for more information about expansion: https://developer.twitter.com/en/docs/twitter-api/expansions
            # for more information about tweet_fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
            self.filter(expansions = 'author_id,referenced_tweets.id,attachments.media_keys,in_reply_to_user_id'
                        , tweet_fields = 'created_at,lang,possibly_sensitive,source,entities,public_metrics')

        except Exception as e:
            print('An Error Occured when running:', e)

    def get_result(self):
        '''return the collected tweets'''
        return self.result



class TwitterCollector():

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.client = tweepy.Client(bearer_token = self.bearer_token)
        self.ts = TwitterStreamer(bearer_token=self.bearer_token)

    def renew_client(self):
        '''renew the client'''
        self.client = tweepy.Client(bearer_token = self.bearer_token)
    
    def fetch_recent_tweets(self, query
                            , tweets_cnt = 100
                            , start_time = None
                            , end_time = None
                            , save_result = True
                            , save_dir = None
                            , file_name = None
                            ):
        '''
        Collecing recent tweets up to 7 days.
        `query`: the search rules. For more information, please see: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md
        `tweets_cnt`: the number of tweets to be collected.
        `start_time`: datetime.datetime type, search posts after this time. Must be within 7 days.
        `end_time`: datetime.datetime type, search posts before this time. Must be within 7 days.
        `save_result`: If True, the result will be saved in a json file in the same directory.
        `save_dir`: The directory you want to save this file. If not specified, the file will be written in the same directory.
        `file_name`: The file name. If not specified, the file will be named after your searh query and tweet count.
        '''
        # renew client first
        self.renew_client()

        tweets_info = []
        tweets = tweepy.Paginator(self.client.search_recent_tweets, query = query, max_results = 100
                                , start_time = start_time
                                , end_time = end_time
                                , expansions = ['author_id', 'referenced_tweets.id', 'geo.place_id', 'attachments.media_keys', 'in_reply_to_user_id']
                                , tweet_fields = ['author_id', 'created_at', 'lang', 'possibly_sensitive', 'source', 'geo', 'entities', 'public_metrics', 'context_annotations']
                                , place_fields = ['country', 'country_code', 'geo']
                                ).flatten(tweets_cnt)
        for tweet in tweets:
            tweets_info.append(tweet.data)

        result = {}
        result['collection_type'] = 'recent post'
        result['collection_timestamp'] = time.time()
        result['query'] = query
        result['tweet_cnt'] = len(tweets_info)
        result['tweets'] = tweets_info

        if save_result:
            # specify directory 
            if not file_name:  # file name not specified
                file_name = 'recent_post_' + query.replace(':','-')+'_'+str(tweets_cnt)+'.json'
            else:
                if '.json' not in file_name:
                    file_name = file_name + '.json'
            if save_dir:
                if not os.path.exists(save_dir):  # make sure the direcroty exists
                    os.makedirs(save_dir)
                save_file = os.path.join(save_dir, file_name)
            else:
                save_file = file_name

            with open(save_file, 'w', encoding = 'utf-8') as w:
                w.write(json.dumps(result, indent=4))

        return result

    def fetch_stream_tweets(self, query
                            , tweets_cnt = 100
                            , show_process = True
                            , save_result = True
                            , save_dir = None
                            , file_name = None
                            ):
        '''Collecing tweets on stream.
        `query`: the search rules. For more information, please see: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md
        `tweets_cnt`: the number of tweets to be collected.
        `show_process`: If True, the tweet collected will be printed in the screen.
        `save_result`: If True, the result will be saved in a json file in the same directory.
        `save_dir`: The directory you want to save this file. If not specified, the file will be written in the same directory.
        `file_name`: The file name. If not specified, the file will be named after your searh query and tweet count.
        '''
        self.ts.collect_tweets_stream(query = query, tweets_cnt = tweets_cnt, show_process = show_process, save_result = save_result, save_dir = save_dir, file_name = file_name)
        result = self.ts.get_result()
        return result


    def fetch_author_info(self, author_id):
        '''Fetch the meta data for the author.
        `author_id`: the id for the author
        '''

        self.renew_client()
        # for more information on user fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
        user = self.client.get_user(id = int(author_id)
                            , user_fields = ['created_at', 'description', 'location', 'public_metrics', 'verified'])
        if user and user.data:
            return user.data.data
        else:
            return None


if __name__ == "__main__":
    bearer_token = r"YOUR_BEARER_TOKEN_HERE"

    # initiate the class
    tc = TwitterCollector(bearer_token=bearer_token)

    # set up search queries
    query1 = 'queen'  # tweets containing the word 'queen'
    query2 = 'queen elizabeth'  # tweets containing 'queen' and 'elizabeth' at the same time
    query3 = 'queen OR elizabeth' # tweets containing 'queen' or 'elizabeth'
    query4 = 'queen OR elizabeth -is:retweet lang:en'  # tweets containing 'queen' or 'elizabeth', written in English, and excluding retweets


    # 1. search for recent tweets posted in the last seven days

    # 1.1 search for recent tweets posted up to 30 seconds ago
    recent_result1 = tc.fetch_recent_tweets(query=query1  # search query
                            , tweets_cnt= 1000  # number of tweets to collect
                            , save_result= True # if True, the result will be atomatically saved to a json file in the current directory for later analysis
                            )
    
    # you can also specify the exact time window for tweet collection
    recent_result2 = tc.fetch_recent_tweets(query=query2  # search query
                            , tweets_cnt= 1000  # number of tweets to collect
                            , save_result= True # if True, the result will be atomatically saved to a json file in the current directory for later analysis
                            , start_time = datetime.fromisoformat('2022-09-15 14:00:00')  # starting time for tweet collection, must be within 7 days
                            , end_time = datetime.fromisoformat('2022-09-15 18:00:00')  # ending time for tweet collection, must be within 7 days
                            , save_dir = 'sample_data'  # the file will be saved in this directory
                            , file_name = 'queen.json'  # this will be the file name
                            )
    

    # 2. search for streaming tweets (ongoing tweets)

    streaming_result = tc.fetch_stream_tweets(query = query4  # search query
                                            , tweets_cnt = 100  # number of tweets to collect. Collection might take a long time depending on the number of tweets to collect and the popularity of the keyword in the query
                                            , show_process= True # if True, the collected tweet will be printed on the panel
                                            , save_result = True  # if True, the result will be atomatically saved to a json file in the current directory for later analysis
                                            )
    

    # 3. Here is the structure of the data obtained
    print(type(streaming_result['tweets']))  # streaming result is stored in a list, where each object is one tweet
    print(streaming_result['tweets'][0])  # tweet information is like this


    # 4. We now know the author id for each post. Let's get the author information according to the author id.
    author_id = streaming_result['tweets'][0]['author_id']  # sample one author
    author_info = tc.fetch_author_info(author_id)
    print(author_info)
