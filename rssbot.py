import feedparser
import urllib.request
import requests
import json
import base64
from bs4 import BeautifulSoup

FEEDS_LIST = "feeds.txt"
WP_CREDS = "wp-creds.txt"  # format as username:password
WP_URL = "https://wordpress.example.com"


# returns an array of strings from the specified file
def get_feed_urls(filename):
  dict_file = open(filename, 'r')
  urls = dict_file.readlines()
  return urls


# posts content to WordPress site
def make_post_wp(title, content):
  wp_auth = ""
  with open("wp-creds.txt") as creds:
    wp_auth = creds.read().replace("\n", '')

  wp_auth = "Basic " + str(base64.standard_b64encode(wp_auth.encode("ascii")))[2:-1]

  print(title)

  rest_api_url = WP_URL + "/wp-content/plugins/creds/newapi.php?"

  content = content.replace("makeArticleAd();", "")  # clean ad scripts

  params = {
    'auth': wp_auth, 
    'title': title, 
    'excerpt': content[:140], 
    'content': content
  }

  t = requests.post(rest_api_url, data=params)
  
  print('Status Code: ' + str(t))


feed_urls = get_feed_urls(FEEDS_LIST)

for url in feed_urls:
  entries = feedparser.parse(url)['entries']
  go = True
  for post in entries:
    if go == True:
      title = post['title']
      link = post['feedburner_origlink']

      html = urllib.request.urlopen(link).read()
      soup = BeautifulSoup(html, 'html.parser')

      # fetch only the article's content
      content = str(soup.find(id="articleText"))

      # cut out related stories section
      if "Related stories" in content:
        content = content[:content.index("Related stories")]

      # post to WordPress blog via rest api
      make_post_wp(title, content)

      go = True
