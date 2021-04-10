import streamlit as st
import streamlit.components.v1 as components
import os
import datetime

LAST_UPDATED = open('last_updated.txt','r').read()

def make_header():
	st.title('Cloudy Headlines')
	st.write("This app displays today's top stories in word cloud form. Last updated {} UTC".format(LAST_UPDATED))
	#st.header('Track media trends visually')

def dropdown():
	options = ('Unigrams','Bigrams')
	selection = st.selectbox('What token length would you like to visualize?',options)
	make_images(options.index(selection))
	

def make_images(selection):
	a,b = st.beta_columns(2)
	columns = [a,b]
	images = [f'clouds/{selection+1}/{x}' for x in os.listdir(f"clouds/{selection+1}") if LAST_UPDATED in x]
	for i,image in enumerate(images):
		columns[i%2].markdown(f'<center> <b>{image.split("-")[0].split("/")[2].upper()}</b> </center>',
			unsafe_allow_html=True)
		columns[i%2].image(image,use_column_width=True)

if __name__ == '__main__':
	
	make_header()
	dropdown()