import pandas as pd
import requests
import datetime
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from PIL import Image, ImageOps
import psycopg2
import os
import boto3


print("Setting up wordcloud generation environment...")
nltk.download('stopwords')


stop_words = set(stopwords.words('english')).union(set(['may','say','says','said','could','new','like','one','two','year','get','still','since','news']))
stop_words.remove('all')
site_specific_stop_words = {'https:www.foxnews.com':['fox'],
                           'https://nytimes.com':['new','york','times']}


print("Reading headlines from Redis")
connection = psycopg2.connect(os.environ['dsn'])
q = """
select *
from (select *,rank() over (partition by domain order by timestamp desc) as r from public.headlines) h
where r = 1
"""
headlines = pd.read_sql(q,connection).replace('', np.nan).dropna()
headlines_dict = {domain:{'stories':list(set(headlines[headlines.domain == domain].headline,)),
                          'timestamp':headlines[headlines.domain == domain].timestamp.max() }for domain in headlines.domain.unique()}


print("Authenticating to S3")
s3 = boto3.resource('s3',region_name = 'us-east-1',aws_access_key_id = os.environ['aws_access_key_id'],aws_secret_access_key = os.environ['aws_secret_access_key'])
bucket = s3.Bucket('cloudy-headlines')


def write_word_clouds(stories_dict,n,min_occurences=0):
    
    plots = []
    if 'mask.png' not in os.listdir('templates'):
      mask_bytes = requests.get('https://gist.githubusercontent.com/teoliphant/7709098/raw/e826895ca1d8d85b20265b6759f1d64086e29dd7/circ_mask.png').content                       
      open('templates/mask.png','wb').write(mask_bytes)
    mask = np.array(ImageOps.invert(Image.open('templates/mask.png')))
    for i,root in enumerate(stories_dict.keys()):
        fig,ax = plt.subplots(figsize=(15,10))
        stories = stories_dict[root]['stories']
        vectorizer = CountVectorizer(ngram_range=(n,n),stop_words = stop_words.union(set(site_specific_stop_words.get(root,[]))))
        bag_of_words = vectorizer.fit_transform(stories)
        frequencies = bag_of_words.sum(axis = 0)
        frequency_dict = {word:frequencies[0, idx] for word, idx in vectorizer.vocabulary_.items() if frequencies[0, idx] > min_occurences}
        
        
        wordcloud = WordCloud(colormap='winter',
                              font_path = 'fonts/MuktaMahee.ttc',
                              prefer_horizontal = .95,
                              mask = mask,
                              scale=1,
                              background_color='white',).generate_from_frequencies(frequencies = frequency_dict)
        
        ax.imshow(wordcloud)
        ax.axis('off')
        d = root.replace("https://","").replace("www.","").replace(".com","").split("/")[0]
        directory = f'clouds/{n}/{stories_dict[root]["timestamp"].strftime("%Y-%m-%dT%HH")}'
        if stories_dict[root]["timestamp"].strftime("%Y-%m-%dT%HH") not in os.listdir(f'clouds/{n}'):
          os.mkdir(directory)
        path = f'{directory}/{d}.jpg'
        plt.savefig(path)
        print("Writing {} to S3".format(path))
        bucket.upload_file(path,path)


for n in [1,2]:
  print("Writing wordclouds for {}-length tokens".format(n))
  write_word_clouds(headlines_dict,n)

