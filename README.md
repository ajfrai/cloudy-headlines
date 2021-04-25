# Cloudy Headlines

A <a href="https://www.waterqualitydata.us/portal/"> streamlit</a> app that displays daily headlines in word cloud form. The application is hosted on Heroku and available <a href="https://nameless-hamlet-76344.herokuapp.com/">here </a>.<br><br>
The data pipeline makes use of Heroku scheduler. Each day, a scheduled task calls an AWS `lambda` function to scrape Washington Post, New York Times, Fox News and CNN headlines. A second scheduled task generates unigram and bigram word clouds and stores them on S3.<br><br>
The word clouds are displayed on the application home page. 

# Future Improvements

Cloudy Headlines is not a complete effort. There are a number of ways this application could improve:
1. The headline scraper could pull headlines from additional news sources.
2. The headline scraper currently pulls data from specific endpoints for the scraped news sources. It's possible that these are not the best endpoints ot hit for these outlets. This merits further investigation.
3. The word cloud generator would benefit from improved language preprocessing.

# Future Features

1. Visitors should have the ability to view 
	- historic clouds
	- unigram and bigram count trends over time
	- full headlines associated with specific tokens
2. We all know word clouds are a very controversial way to visualize natural language data. The website should provide a detailed disclaimer.
