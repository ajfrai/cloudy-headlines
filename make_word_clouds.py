import pandas as pd
import requests
import datetime
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from PIL import Image, ImageOps
import psycopg2
import os

nltk.download('stopwords')


stop_words = set(stopwords.words('english')).union(set(['may','say','says','said','could','new','like','one','two','year','get','still','since']))
stop_words.remove('all')
site_specific_stop_words = {'https:www.foxnews.com':['fox'],
                           'https://nytimes.com':['new','york','times']}


connection = psycopg2.connect(os.environ['dsn'])
headlines = pd.read_sql('select domain,headline,timestamp from public.headlines',connection).replace('', np.nan).dropna()
headlines_dict = {domain:{'stories':list(set(headlines[headlines.domain == domain].headline,)),
                          'timestamp':headlines[headlines.domain == domain].timestamp.max() }for domain in headlines.domain.unique()}
def word_clouds(stories_dict,n,min_occurences=0):
    
    plots = []
    mask_bytes = requests.get('https://gist.github.com/teoliphant/7709098/raw/e826895ca1d8d85b20265b6759f1d64086e29dd7/ell_mask.png').content                       
    open('mask.png','wb').write(mask_bytes)
    mask = np.array(ImageOps.invert(Image.open('mask.png')))
    for i,root in enumerate(stories_dict.keys()):
        fig,ax = plt.subplots(figsize=(15,10))
        stories = stories_dict[root]['stories']
        vectorizer = CountVectorizer(ngram_range=(n,n),stop_words = stop_words.union(set(site_specific_stop_words.get(root,[]))))
        bag_of_words = vectorizer.fit_transform(stories)
        frequencies = bag_of_words.sum(axis = 0)
        frequency_dict = {word:frequencies[0, idx] for word, idx in vectorizer.vocabulary_.items() if frequencies[0, idx] > min_occurences}
        
        
        wordcloud = WordCloud(colormap='winter',
                              font_path = '/System/Library/Fonts/MuktaMahee.ttc',
                              prefer_horizontal = .95,
                              mask = mask,
                              scale=1,
                              background_color='white',).generate_from_frequencies(frequencies = frequency_dict)
        
        ax.set_title(root)
        ax.axis('off')
        d = root.replace("https://","").replace("www.","").replace(".com","").split("/")[0]
        path = f'clouds/{n}/{d}-{stories_dict[root]["timestamp"].strftime("%Y-%m-%dT%HH")}.png'
        plt.savefig(path)

for n in [1,2]:
	word_clouds(headlines_dict,n)
