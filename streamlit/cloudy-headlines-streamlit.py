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
import boto3

s3 = boto3.resource('s3',region_name = 'us-east-1',aws_access_key_id = os.environ['aws_access_key_id'],aws_secret_access_key = os.environ['aws_secret_access_key'])
bucket = s3.Bucket(os.environ['aws_bucket_name'])




def make_header():
	st.title('Cloudy Headlines')
	st.write("This app displays today's top stories in word cloud form.")
	
	#st.header('Track media trends visually')

def slider():
	filter = bucket.objects.filter(Prefix=f'clouds/1')
	last_date = sorted([datetime.datetime.strptime(x.key.split("/")[2],"%Y-%m-%dT%HH") for x in filter],reverse=True)[0]
	chosen_date = st.slider(
		"Which date would you like to view headlines for:",
		value=last_date,
		max_value=last_date,
		min_value=datetime.datetime.strptime("2021-04-12T12H","%Y-%m-%dT%HH"),
		format="MM/DD/YY"
	)
	return datetime.datetime.strftime(chosen_date,'%Y-%m-%d')

def cloud_selector():
	date = slider()
	options = ('Unigrams','Bigrams')
	token_len = st.selectbox('What token length would you like to visualize?',options)
	make_images(options.index(token_len)+1,date)
	

def make_images(token_len,date):
	a,b = st.beta_columns(2)
	columns = [a,b]
	filter = bucket.objects.filter(Prefix=f'clouds/1')
	date = [x.key.split("/")[2] for x in filter if date in x.key][0]
	images = bucket.objects.filter(Prefix='clouds/{}/{}/'.format(token_len,date))
	bucket_path = f'https://s3.amazonaws.com/{os.environ["aws_bucket_name"]}'
	for i,image in enumerate(images):
		
		columns[i%2].markdown(f'<center> <b>{image.key.split("/")[3].split(".")[0].upper()}</b> </center>',
			unsafe_allow_html=True)
		
		image_path = f"{bucket_path}/{image.key}"
		
		columns[i%2].image(image_path,use_column_width=True)
	st.write("Last updated: {} UTC".format(date.replace("T"," @ ").replace("H","")))


if __name__ == '__main__':
	make_header()
	cloud_selector()


