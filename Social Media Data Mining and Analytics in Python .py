#!/usr/bin/env python
# coding: utf-8

# The purpose of the project was to analyze and draw insights from data extracted from Twitter using Twitter APIs 
# that mentioned “BORN PINK”. Background information: “BORN PINK” is the second studio album by South Korean girl group Blackpink, released on September 16, 2022. 
# 
# Questions I was interested in : 
# 
# 1) How many tweets were tweeted 2 weeks after the album was released. Did the number of tweets drop after 2 weeks?                           
# 
# 2) What people talked about in these tweets ? What were the most common words people mentioned in these tweets ? Did they use hashtags and @ anyone in these tweets? 
# 
# 3）Which tweets about “BORN PINK” were the most popular and had been replied to/ re-tweeted by Twitter users for the most times within this time window ? What these tweets say about Blackpink and “BORN PINK”
# 
# 4) Who were the most influential Twitter users that tweeted about “BORN PINK” within this time window 
# 
# 5) Based on the sentiment analysis, what were people's reaction to this new album 
# 
# 6) What were some other interesting insights presented in data visualizations and analysis

# In[1]:


get_ipython().system('pip install tweepy')


# In[2]:


import tweepy


# ## Data extraction from Twitter through Twitter APIs
# 
# 

# In[3]:


# TwitterCollector was a python package developed by professor to extra Twitter data through APIs and was provided in the folde

from TwitterCollector import TwitterCollector 


# In[4]:


from datetime import datetime


# In[5]:


bearer_token = r"AAAAAAAAAAAAAAAAAAAAADXLhgEAAAAAfMIjSqqTKZSDwLutbnv3c6MlZXk%3DPuusgIUjFsk9beNf70hI3Pmzxuc5uCoK90UT7lFKc0EkFX670a"


# In[6]:


tc = TwitterCollector(bearer_token = bearer_token)


# In[7]:


query='"BORN PINK" -is:retweet lang:en'  # The Key words i was interested in 


# In[8]:


# Initially the following code was executed get data from twitter. I was interested in Tweets that mentioned 
# “BORN PINK” from 2022-09-28 to 2022-10-02 and only needed 10000 of them. The output was saved in a JSON file, named bp.json and 
# is provided in the folder. 


#recent_tweets = tc.fetch_recent_tweets(query = query  
                                        #, tweets_cnt = 10000
                                        #, save_result = True 
                                        #, start_time = datetime.fromisoformat('2022-09-28 00:00:00')
                                        #, end_time = datetime.fromisoformat('2022-10-02 00:00:00')
                                        #, file_name = 'bp.json'  # this will be the file name
                                        #)


# In[9]:


import json
import pprint as pp


# In[10]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[11]:


with open("bp.json") as json_file:
    json_data=json.load(json_file)

print(type(json_data))


# In[12]:


json_data.keys()


# In[13]:


#get unique author id, 

unique_author_list=[]
for i in range(len(json_data['tweets'])):
        if json_data['tweets'][i]["author_id"] not in unique_author_list:
            unique_author_list.append(json_data['tweets'][i]["author_id"])

print(unique_author_list[0:10])
print(len(unique_author_list))


# In[14]:


#The following code was used initially to retrieve author information from Twitter. Since the running time will last for hours, here I saved the results into a
# Json file author_info_list.json which is provided in the folder 

#get author_info
#import time
#author_info_list=[]
#for i in unique_author_list:
    #try:
        #author_info=tc.fetch_author_info(i)
        #author_info_list.append(author_info)
    #except tweepy.TooManyRequests:
        #print(len(author_info_list))
        #print("Wait for 15 mins.")
        #time.sleep(15*60)

#print(author_info_list[0])

 


# In[15]:


with open("author_info_list.json") as json_file:
    author_info_list=json.load(json_file)

print(type(author_info_list))


# In[17]:


pp.pprint(author_info_list[0:3])


# In[18]:


get_ipython().system('pip install clean-text')


# ## Data cleaning and transformation

# In[19]:


# Data cleaning: step 1 Identified the symbols and numbers and replaced them with space, preparing for the next step of data cleaning

from collections import Counter
from cleantext import clean #clean the emoji 
import string
puncs = string.punctuation
dgts = string.digits
table_dp = str.maketrans(dgts + puncs, (len(dgts)+len(puncs)) * " ")


# In[20]:


# Data Cleaning: Step 2: cleaned the emojis and separated the words by space.

# In this step I kept the stopwords as I wanted to compare the word counts with the next step where the stopwords were removed

word_list=[]
for i in range(len(json_data['tweets'])):
    a=json_data['tweets'][i]['text']
    b=clean(a,no_emoji=True)
    c=b.split("http")
    d=c[0]
    e=d.translate(table_dp)
    f=e.split()
    word_list.extend(f)

#print(word_list)
e=Counter(word_list)
e.most_common(10)


# In[21]:


# Data Cleaning: Step 3, Removed stopwords. Here some of the common stopwords were provided in the file "stopwords.pkl"
# However, based on the nature of my data, i added in more stopwords to the list and excluded them all together with the common ones from the tweets when i counted the most mentioned words 

import pickle

# The p list contained the new stowpwords I added in 

p=['sell','still','say','yeah','already','please','let','said','pls','every','rfs','wts','lfb','ver','need',"pcs",'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
with open('stopwords.pkl','wb') as f:
    pickle.dump(p,f)
    f.close

with open('stopwords.pkl','rb') as f:
    stopwords = pickle.load(f)
    
#print(stopwords)

word_list2=[]
for i in word_list:
    if i not in stopwords and len(i)>2:
        word_list2.append(i.lower())

#print(word_list2)
d2=Counter(word_list2)
d2.most_common(10)


# ## Primary data analysis 

# In[22]:


# Hashtag is a common use on Twitter. In this step, I analyzed the most popular hashtags in tweets that mentioned "BORN PINK"

hashtag=[]
for i in range(len(json_data['tweets'])):
    word_list3=clean(json_data['tweets'][i]["text"],no_emoji=True).split()
    for i in word_list3:
        if "#" in i:
            hashtag.append(i)
#print(hashtag)
d3=Counter(hashtag)
d3.most_common(10)


# In[23]:


# Following last step, i was interested to know what were the most popular "@"


at=[]
for i in range(len(json_data['tweets'])):
    word_list4=clean(json_data['tweets'][i]["text"],no_emoji=True).split()
    for i in word_list4:
        if "@" in i:
            at.append(i)

#print(at)
d4=Counter(at)
d4.most_common(10)


# In[24]:


# What did most of the tweets come from

sourcelist=[]
for i in range(len(json_data['tweets'])):
    source=json_data['tweets'][i]["source"]
    #print(type(source))
    #print(source)
    sourcelist.append(source)

#print(sourcelist)
source1=Counter(sourcelist)
source1.most_common(3)


# ## Descriptive analysis, identifying patterns and trend in data

# In[25]:


import nltk
nltk.download('punkt')


# In[26]:


# I was interested to know when most tweets were created and if the numnber of tweets dropped 2 weeks after the album was released 
# This visual also shed light on the time trend of the tweet counts

get_ipython().run_line_magic('matplotlib', 'inline')
#print(json_data['tweets'][0]['created_at'])
datelist=[]
for i in range(len(json_data['tweets'])):
    date=json_data['tweets'][i]["created_at"]
    date1=date.split("T")
    date2=date1[0]
    datelist.append(date2)

#print(datelist)
source2=Counter(datelist)
source2.most_common(3)


# In[27]:


freq=nltk.FreqDist(datelist)
freq.plot(3)


# In[28]:


# Which were the three most influential tweets and what they said about "BORN PINK". These tweets had been replied to 
# and re-tweeted for the most times by other users 



social_influence={}
socialtotallist=[]
for i in range(len(json_data['tweets'])):
    v=json_data['tweets'][i]["public_metrics"]
    tweetsid=json_data['tweets'][i]["id"]
    socialtotal=0
    for i in v:
        socialtotal=socialtotal+v[i]
    socialtotallist.append(socialtotal)
    social_influence[tweetsid]=socialtotal
    
a=sorted(socialtotallist,reverse=True)
#print(a)
for n in range(0,3):
    for m in range(len(json_data['tweets'])):
        if social_influence[json_data['tweets'][m]["id"]]==a[n]:
            print(json_data['tweets'][m]['text']+" - "+str(a[n]))
    


# In[29]:


# who were the most frequently tweeting authors among these tweets? 


user_id_list=[]
for i in range(len(json_data['tweets'])):
    a=json_data['tweets'][i]['author_id']
    #print(a)
    user_id_list.append(a)

#sorted(user_id_list,reverse=True)
#print(user_id_list)
u=Counter(user_id_list)
u.most_common(3)


# In[30]:


# This extra step of data cleaning was executed to remove the null data in the author_info_list as i realized null values 
# would affect the analysis in the next step 


for i in author_info_list:
    if i is None:
        author_info_list.remove(i)
print(len(author_info_list))


# In[31]:


# Who were the three most influential authors? The influential score was measured as the sum of number of followers, 
# number of people they followed, number of tweets they posted and numher of their tweets that were listed by others

user_influence={}
usertotallist=[]
for i in range(len(author_info_list)):
    v=author_info_list[i]['public_metrics']
    userid=author_info_list[i]['username']
    usertotal=0
    for i in v:
        usertotal=usertotal+v[i]
    usertotallist.append(usertotal)
    user_influence[userid]=usertotal
    
u=sorted(usertotallist,reverse=True)
#print(u)
#user_influence
for n in range(0,3):
    for m in range(len(author_info_list)):
        if user_influence[author_info_list[m]['username']]==u[n]:
            print(author_info_list[m]['username']+" - "+str(u[n]))


# ## Data visualization that revealed interesting insights

# In[32]:


# Created word cloud in order to better visualize the pattern in data and draw insights

get_ipython().system('pip install wordcloud')


# In[33]:


from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk

get_ipython().run_line_magic('matplotlib', 'inline')


# In[34]:


word_list2_string=' '.join(word_list2)
word_list2_string[:100]


# In[35]:


# lower max_font_size
wordcloud = WordCloud(width=800, height=400,collocations=False).generate(word_list2_string) # note that text is a string, not a list

# Display the generated image:
plt.figure(figsize=(20,10)) # set up figure size
plt.imshow(wordcloud) # word cloud image show
plt.axis("on") # turn on axis
plt.savefig('my_word_cloud.png') # save as PNG file
plt.savefig('my_word_cloud.pdf') # save as PDF file
plt.show()  # show in Jupyter notebook


# ## Sentiment Analysis : what people's reactions are to this new album

# In[36]:



get_ipython().system('pip install textblob')


# In[37]:


from textblob import TextBlob


# In[38]:


# calculate the average polarity and subjectivity scores for the collected tweets

polarity=[]
subjectivity=[]
polarity_dic={}
for i in range(len(json_data['tweets'])):
    x=json_data['tweets'][i]['text']
    x1=clean(x,no_emoji=True)
    x2=x1.split('https')
    x3=x2[0]
    tb=TextBlob(x3)
    polarity.append(tb.sentiment.polarity)
    subjectivity.append(tb.sentiment.subjectivity)
    polarity_dic[x3]=tb.sentiment.polarity
#print(polarity)
#print(subjectivity)
print(str(sum(polarity)/len(polarity)))
print(str(sum(subjectivity)/len(subjectivity)))


# In[39]:


# Visualized the polarity and subjectivity score distributions using histograms


import matplotlib.pyplot as plt

plt.hist(polarity, bins=10)

plt.xlabel('score')
plt.ylabel('tweet count')
plt.grid(True)
plt.savefig('polarity.pdf')
plt.show()


# In[40]:


plt.hist(subjectivity, bins=10)

plt.xlabel('score')
plt.ylabel('tweet count')
plt.grid(True)
plt.savefig('subjectivity.pdf')
plt.show()


# In[41]:


ranklist=sorted(polarity)


# In[42]:


# Based on the polarity scores, what are the most negative tweets
ranklist=sorted(polarity)
for key in polarity_dic.keys():
    if polarity_dic[key]==ranklist[0]:
        print(key+" "+str(ranklist[0]))


# In[43]:


# Based on the polarity scores, what are the most postive tweets

ranklist=sorted(polarity)
for key in polarity_dic.keys():
    if polarity_dic[key]==ranklist[-1]:
        print(key+" "+str(ranklist[-1]))


# In[44]:


# What was the lowest sentiment score among the top 150 sentiment scores 


r=Counter(ranklist)
r.most_common(150)[-1:]


# In[45]:


# Since i realized the lowest was -0.275, here I wanted to look at tweets with that score


ranklist=sorted(polarity)
for key in polarity_dic.keys():
    if polarity_dic[key]== -0.275:
        print("/n"+key+" "+str(-0.275))


# ## The insights drawn from analysis and visualizations 

# 1. Among 7 songs (‘Pinkvenom’, ‘Shutdown’, and ‘The Happiest Girls’, ‘Typa Girl’, ‘Yeah Yeah Yeah, ‘Hard to Love’, ‘The Happiest Girl’, ‘Tally’, and ‘Ready for Love’) in the albums, ‘Pinkvenom’, ‘Shutdown’, and ‘The Happiest Girls’ are the top 3 songs of the album. For that, i would recommend Blackpink consider covering these three songs in their upcoming concerts. Even more, YG Entertainment, Blackpink’s agency, can utilize these three songs to promote the upcoming world tour and further understand the preference for music genres among global audiences to make sure that the “next” album will still be a trending topic.

# 2. Billboard was mentioned quite a lot as suggested by World cloud, which illustrates that ‘BORN PINK’ has been a trending topic on Billboard. In fact, the ‘BORN PINK’ album ranks at NO.1 on the latest Billboard 200 chart (Billboard, 2022). Moreover, BORN PINK is the only album by K-pop groups on the Billboard chart, illustrating that Blackpink’s phenomenon has spread around the world. In other words, K-pop successfully shifts from a regional music trend to worldwide music culture
