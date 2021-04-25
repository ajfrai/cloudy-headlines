import os
from bs4 import BeautifulSoup
import requests
import datetime
import psycopg2
import hashlib

import json


def test_internet_connection():
  root = 'https://washingtonpost.com'
  soup = BeautifulSoup(requests.get(root).text,features = 'html.parser')
  return [x['href'] for x in soup.findAll('a',href = True)]

def grab_headlines(connection):
  
  cursor = connection.cursor()

  roots = ['https://washingtonpost.com',
           'https://www.foxnews.com',
           'https://nytimes.com',
           'https://www.cnn.com/data/ocs/section/index3.html:homepage-magellan-zone-1/views/zones/common/zone-manager.izl']

  year = datetime.datetime.today().year


  ### define rules dict

  wapo_rule = lambda root,obj: '/' in obj['href'] and str(year) in obj['href'] and root in obj['href']
  fox_news_rule = lambda root,obj: '-' in obj['href'] and root in obj['href']
  nytimes_rule = lambda root,obj: '/' in obj['href'] and \
                                  str(year) in obj['href'] and (obj['href'][0] == "/" or root in obj['href']) and len(obj.findAll('img')) == 0
  cnn_rule = lambda root,obj: '/' in obj['href'] and \
                                  str(year) in obj['href'] and (obj['href'].replace('\\"','')[0] == "/" or root in obj['href'])


  rules_dict = {
      'https://www.foxnews.com':fox_news_rule,
      'https://washingtonpost.com':wapo_rule,
      'https://nytimes.com':nytimes_rule,
      'https://www.cnn.com/data/ocs/section/index3.html:homepage-magellan-zone-1/views/zones/common/zone-manager.izl':cnn_rule
  }

  site_specific_stop_words = {
      'https://nytimes.com':['new','york','times'],
      'https://www.foxnews.com':['fox']
  }

  def is_story(root,obj,rules_dict):
      root_shortened = root.replace("www.","").split("/")[2]
      site_specific_rule = rules_dict.get(root,lambda root_shortened,obj: root_shortened in obj['href'])
      
      return site_specific_rule(root_shortened,obj)



  for root in roots:
      """
      schema
      headline_id | headline | href | domain | timestamp
      """
      
      now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      soup = BeautifulSoup(requests.get(root).text,features = 'html.parser')
      stories = list(set([(hashlib.md5('{}{}{}'.format(x.getText(separator=" "),root,now).encode('utf-8')).hexdigest(),
                           x.getText(separator=" ").replace("'",""),
                           x['href'],
                           root,
                           now
                           ) for x in soup.findAll('a',href=True) if is_story(root,
                                                                              x,
                                                                              rules_dict)]))
      for story in stories:
          cursor.execute(f"insert into public.headlines (headline_id, headline, href, domain, timestamp) values ('{story[0]}', '{story[1]}','{story[2]}','{story[3]}',to_timestamp('{story[4]}','YYYY-MM-DD HH24:MI:SS'));")
      connection.commit()

  connection.close()


def lambda_handler(event, context):
    connection = psycopg2.connect(os.environ['dsn'])
    connection.set_session(autocommit = True)
    action = event.get('action','test_connection')
   
    if action == 'test_connection':
      
      cursor = connection.cursor()
      cursor.execute('select * from public.test limit 1')
      connection.commit()
      body = cursor.fetchone()
    #grab_headlines(connection)
      return {
          'statusCode': 200,
          'body': json.dumps('Collected the test data! {}'.format(body))
      }

    elif action == 'test_internet_connection':
      return {
          'statusCode': 200,
          'body': json.dumps({'links':test_internet_connection()})
      }

    elif action == 'grab_headlines':
      grab_headlines(connection)
      return {
          'statusCode': 200,
          'body': json.dumps('Grabbed the headlines!')
      }
