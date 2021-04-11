import streamlit as st
import streamlit.components.v1 as components
import os
import datetime

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


def make_word_clouds():
	nltk.download('stopwords')


	stop_words = set(stopwords.words('english')).union(set(['may','say','says','said','could','new','like','one','two','year','get','still','since','news']))
	stop_words.remove('all')
	site_specific_stop_words = {'https:www.foxnews.com':['fox'],
	                           'https://nytimes.com':['new','york','times']}


	connection = psycopg2.connect(os.environ['dsn'])
	q = """
	select *
	from (select *,rank() over (partition by domain order by timestamp desc) as r from public.headlines) h
	where r = 1
	"""
	headlines = pd.read_sql(q,connection).replace('', np.nan).dropna()
	headlines_dict = {domain:{'stories':list(set(headlines[headlines.domain == domain].headline,)),
	                          'timestamp':headlines[headlines.domain == domain].timestamp.max() }for domain in headlines.domain.unique()}
	def word_clouds(stories_dict,n,min_occurences=0):
	    
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
	        path = f'clouds/{n}/{d}-{stories_dict[root]["timestamp"].strftime("%Y-%m-%dT%HH")}.jpg'
	        open('streamlit/last_updated.txt','w').write(stories_dict[root]["timestamp"].strftime("%Y-%m-%dT%HH"))

	        plt.savefig(path)

	for n in [1,2]:
		word_clouds(headlines_dict,n)

def make_header():
	st.title('Cloudy Headlines')
	st.write("This app displays today's top stories in word cloud form.")
	st.write("Last updated: {} UTC".format(LAST_UPDATED.replace("T"," @ ").replace("H","")))
	#st.header('Track media trends visually')

def dropdown():
	options = ('Unigrams','Bigrams')
	selection = st.selectbox('What token length would you like to visualize?',options)
	make_images(options.index(selection))
	

def make_images(selection):
	a,b = st.beta_columns(2)
	columns = [a,b]
	images = [f'streamlit/clouds/{selection+1}/{x}' for x in os.listdir(f"streamlit/clouds/{selection+1}") if LAST_UPDATED in x]
	for i,image in enumerate(images):
		columns[i%2].markdown(f'<center> <b>{image.split("-")[0].split("/")[3].upper()}</b> </center>',
			unsafe_allow_html=True)
		columns[i%2].image(image,use_column_width=True)

LAST_UPDATED = open('streamlit/last_updated.txt','r').read().replace("\n","")

if __name__ == '__main__':
	if datetime.datetime.strptime(LAST_UPDATED,"%Y-%m-%dT%HH").date() < datetime.datetime.today().date():
		word_cloud_state = st.text('Generating word clouds...')
		make_word_clouds()
		LAST_UPDATED = open('streamlit/last_updated.txt','r').read().replace("\n","")
		word_cloud_state = st.text('')


	make_header()
	dropdown()


