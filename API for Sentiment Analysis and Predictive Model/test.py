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
    new_df = old_df[['url', 'campaignTitle', 'success', 'mainCategory', 'category', 'totWordCount', 'numImages', 'percentageGoal']].copy() #create a new dataframe with only url as column

    return new_df

if __name__ == "__main__":
    original_df = create_df("./Kickstarter_preprocessed.csv")
    sentiment_df = create_df("./kickstarter_data.csv")

    df.to_csv(path_or_buf='kickstarter_data.csv', mode='w', header=True )



