#Guardian API Key: 26f27354-93d1-4359-9cd5-5c463c222cca
#NYT API Key: 93d266f3131f4d33b80ece326d3875b5

import re
import json
import urllib.request
import urllib.parse
import lxml.html
from google.cloud import language

#pass in a query term (single keyword works best), returns average sentiment score
def get_guardian(query):
    page_size = 50 #maximum 50
    article_bodies = []
    sentiment_scores = []
    query = urllib.parse.quote_plus(query) #puts string into url query form
    print(query)
    print()

    #searches for query, english language, in year 2017, with page_size number of results
    result = json.loads(urllib.request.urlopen("https://content.guardianapis.com/search?q=%s&lang-en&from-date=2017-01-01&page-size=%d&show-fields=body&api-key=26f27354-93d1-4359-9cd5-5c463c222cca" % (query, page_size)).read())

    for element in result['response']['results']:
        #remove html tags from each article body
        raw_text = lxml.html.document_fromstring(element['fields']['body']).text_content() 

        #remove all urls
        raw_text = re.sub(r"http\S+", "", raw_text)

        #add cleaned text to list
        #article_bodies.append(raw_text)
        sentiment_scores.append(sentiment_analysis(raw_text))

    total_magnitude = 0
    total_score = 0
    for sentiment in sentiment_scores:
        print(sentiment.score, sentiment.magnitude)
        total_score += sentiment.score
        total_magnitude += sentiment.magnitude
    
    average_score = total_score / page_size
    average_magnitude = total_magnitude / page_size
    return average_score, average_magnitude


def get_NYT(query):
    query = urllib.parse.quote_plus(query)
    #searches for query, english language, in year 2017, with page_size number of results
    result = json.loads(urllib.request.urlopen("https://api.nytimes.com/svc/search/v2/articlesearch.json?q=%s&api-key=93d266f3131f4d33b80ece326d3875b5" % (query)).read())

#returns sentiment of a text
def sentiment_analysis(text):
    client = language.Client()
    document = client.document_from_text(text)
    sent_analysis = document.analyze_sentiment()
    dir(sent_analysis)
    sentiment = sent_analysis.sentiment

    return sentiment



if __name__ == "__main__":
    get_NYT("iPhone")
    #score, magnitude = get_guardian("drone")
    #print(score)
    #print(magnitude)



