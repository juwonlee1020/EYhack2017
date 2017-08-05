import time

from tabulate import tabulate
import pandas as pd
import numpy as np

from google.cloud import language

from bs4 import BeautifulSoup
import requests
import lxml.html
import re

def create_df(filepath):
    old_df = pd.read_csv(filepath) #read csv into dataframe
    new_df = old_df[['url', 'campaignTitle', 'success', 'mainCategory', 'category', 'totWordCount', 'numImages', 'continent']].copy() #create a new dataframe with only url as column
    new_df['sentiment_score'] = 0.0 #create sentiment score column
    new_df['sentiment_magnitude'] = 0.0 #create sentiment magnitude column

    return new_df

def sentiment_analysis(text):
    client = language.Client()

    try:
        document = client.document_from_text(text)
        sent_analysis = document.analyze_sentiment()
        dir(sent_analysis)
        sentiment = sent_analysis.sentiment
    except: 
        print("Exception in sentiment_analysis")
        text = " "
        document = client.document_from_text(text)
        sent_analysis = document.analyze_sentiment()
        dir(sent_analysis)
        sentiment = sent_analysis.sentiment
    else:
        print("Non-exception error in sentiment_analysis")
        sentiment = ""
    return sentiment

def scrape(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    html = soup.find("div", class_="full-description") #producet description is only one with this tag. can also use class_=["full-description", "js-full-description", "responsive-media-formatted-lists"]
    text = lxml.html.document_fromstring(str(html)).text_content() 
    text = re.sub(r'(?<!\n)\n(?!\n)|\n{3,}', '\n\n', text)
    
    return text

if __name__ == "__main__":
    df = create_df("./Kickstarter_preprocessed.csv")
    rownum = 0
    for row in df.itertuples():
        '''
        if df.iloc[rownum, 7] != "North America":
            print("Row skipped - " + df.iloc[rownum, 7])
            rownum += 1
            continue
        '''
        start = time.time()
        url = str(df.iloc[rownum, 0])
        text = scrape(url)
        sentiment = sentiment_analysis(text)
        df.set_value(rownum, 'sentiment_score', sentiment.score)
        df.set_value(rownum, 'sentiment_magnitude', sentiment.magnitude)
        rownum += 1
        end = time.time()
        print(str(rownum) + " (" + str(sentiment.score) + ", " + str(sentiment.magnitude) + ") - " + str(end - start))

    print(tabulate(df, headers='keys', tablefmt='psql'))
    df.to_csv(path_or_buf='kickstarter_data.csv', mode='w', header=True )



