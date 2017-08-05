#!flask/bin/python
from flask import Flask
from flask_restful import reqparse
import json

from sklearn.model_selection import train_test_split #To split our data into train & test
from sklearn.ensemble import RandomForestClassifier #To train our model
from sklearn.metrics import classification_report, confusion_matrix #To see how accurate our model is

import numpy as np
import pandas as pd
import seaborn as sns

from google.cloud import language

app = Flask(__name__)

@app.route('/')
def index():
    return "RESTful API"

@app.route('/sentiment_analysis', methods=['GET'])
def sentiment_analysis():
    parser = reqparse.RequestParser()
    parser.add_argument("query")

    args = parser.parse_args()
    text = args.get("query") 

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
    result = {"score" : sentiment.score, "magnitude" : sentiment.magnitude}
    result = json.dumps(result)
    return result

@app.route('/predictive_model', methods=['GET'])
def predict():

###-----PARAMETER HANDLING-----###
    '''
    example url:
    http://localhost:5000/predictive_model?
    mainCategory=Food&category=Drinks&goal=15000&duration=15.4&numPerks=3&
    medianPerk=4.3&estimatedDelivery=200.4&mainVideo=1&numSuccessfulCampaigns=0&
    facebookFriends=234&numCollaborators=13&totWordCount=236&numImages=6
    '''
    #takes in get queries 
    parser = reqparse.RequestParser()
    parser.add_argument("mainCategory")
    parser.add_argument("category")
    parser.add_argument("goal", type=float)
    parser.add_argument("duration", type=float)
    parser.add_argument("numPerks", type=float)
    parser.add_argument("medianPerk", type=float)
    parser.add_argument("estimatedDelivery", type=float)
    parser.add_argument("mainVideo", type=float)
    parser.add_argument("numSuccessfulCampaigns", type=float)
    parser.add_argument("facebookFriends", type=float)
    parser.add_argument("numCollaborators", type=float)
    parser.add_argument("totWordCount", type=float)
    parser.add_argument("numImages", type=float)

    #stores query values to local variables
    args = parser.parse_args()
    mainCategory = args.get("mainCategory") 
    category = args.get("category") 
    goal = args.get("goal") 
    duration = args.get("duration") 
    numPerks = args.get("numPerks") 
    medianPerk = args.get("medianPerk") 
    estimatedDelivery = args.get("estimatedDelivery") 
    mainVideo = args.get("mainVideo") 
    numSuccessfulCampaigns = args.get("numSuccessfulCampaigns") 
    facebookFriends = args.get("facebookFriends") 
    numCollaborators = args.get("numCollaborators") 
    totWordCount = args.get("totWordCount") 
    numImages = args.get("numImages") 

###-----DATAFRAME HANDLING-----###
    #initializes a dataframe for the passed in models
    #d = {"category" : [category], "goal" : [goal], "duration" : [duration], "numPerks" : [numPerks], "medianPerk" : [medianPerk], "estimatedDelivery" : [estimatedDelivery], "mainVideo" : [mainVideo], "numSuccessfulCampaigns" : [numSuccessfulCampaigns], "facebookFriends" : [facebookFriends], "numCollaborators" : [numCollaborators], "totWordCount" : [totWordCount], "numImages" : [numImages]}
    d = {"category" : category, "goal" : goal, "duration" : duration, "numPerks" : numPerks, "medianPerk" : medianPerk, "estimatedDelivery" : estimatedDelivery, "mainVideo" : mainVideo, "numSuccessfulCampaigns" : numSuccessfulCampaigns, "facebookFriends" : facebookFriends, "numCollaborators" : numCollaborators, "totWordCount" : totWordCount, "numImages" : numImages}
    my_data = pd.Series(d)
    ###CATEGORIZING THIS IS FUCKED UP (but still kinda works (since there's only 1 row, "category" = 0))
    #my_df["category"] = pd.Categorical(my_df["category"]).codes
    my_data["category"] = 0.0
    print(my_data)  

    #sets up kickstarter dataframe
    kickstarter_data = pd.read_csv("Kickstarter_preprocessed.csv")
    no_need = ["Unnamed: 0","url", "urlProfile", "url", "campaignTitle", "aggregatedPerkValue","creator", "location","totalNumberBackers", "numComments","numUpdates","totalPledge","backed","comments","created","joinKS","urlCreator","websites","countryState","city","projectsWeLove","continent","valuta","lowestPerkPriceOriginal","noFacebookFriends","pastSuccessRate","numAdditionalVideos","viewGallery","addedPerks","endDate","startDate","experience","percentageGoal","numLiveCampaigns","averageBackersRequired","canceled","highestPerk","lowestPerk","overPaying","shippingWorld","numCompetitors"]
    kickstarter = kickstarter_data.copy() #kickstarter_data remains the same
    kickstarter.drop(no_need, axis=1, inplace=True)
    kickstarter = kickstarter[["mainCategory","category","goal","duration","numPerks","medianPerk","estimatedDelivery","mainVideo","numSuccessfulCampaigns","facebookFriends","numCollaborators","totWordCount","numImages", "success"]]

    #splits dataframe into different main categories
    kc_film_video = kickstarter[kickstarter["mainCategory"]=="Film & Video"].copy()
    kc_publishing = kickstarter[kickstarter["mainCategory"]=="Publishing"].copy()
    kc_design = kickstarter[kickstarter["mainCategory"]=="Design"].copy()
    kc_art = kickstarter[kickstarter["mainCategory"]=="Art"].copy()
    kc_food = kickstarter[kickstarter["mainCategory"]=="Food"].copy()
    kc_fashion = kickstarter[kickstarter["mainCategory"]=="Fashion"].copy()
    kc_games = kickstarter[kickstarter["mainCategory"]=="Games"].copy()
    kc_theater = kickstarter[kickstarter["mainCategory"]=="Theater"].copy()
    kc_music = kickstarter[kickstarter["mainCategory"]=="Music"].copy()
    kc_crafts = kickstarter[kickstarter["mainCategory"]=="Crafts"].copy()
    kc_technology = kickstarter[kickstarter["mainCategory"]=="Technology"].copy()
    kc_comics = kickstarter[kickstarter["mainCategory"]=="Comics"].copy()

    #creates list of dataframes and converts categories to numerical
    kc_dfs = [kc_film_video, kc_publishing, kc_design, kc_art, kc_food, kc_fashion, kc_games, kc_theater, kc_music, kc_crafts, kc_technology, kc_comics]
    for df in kc_dfs:
        df["category"] = pd.Categorical(df["category"]).codes  

###-----MODEL TRAINING-----###
    #create a list of models
    model_list = []
    X_test_list = []
    y_test_list = []

    #train the models
    i = 0
    for df in kc_dfs:
        #Set X (independent vars) and y(dependent vars)
        X = df.drop(["mainCategory", "success"], axis=1)
        y = df['success']
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3)
        #Store test data into the lists so that we can use them outside of the function
        #Each X_test_list element is a dataframe
        X_test_list.append(X_test)
        y_test_list.append(y_test)
        rfc = RandomForestClassifier(n_estimators=200)
        rfc.fit(X_train,y_train)
        model_list.append(rfc)

    #Select appropriate model for the mainCategory
    model = model_list[2]
    if mainCategory == "Film & Video":
        model = model_list[0]
    elif mainCategory == "Publishing":
        model = model_list[1]
    elif mainCategory == "Design":
        model = model_list[2]
    elif mainCategory == "Art":
        model = model_list[3]
    elif mainCategory == "Food":
        model = model_list[4]
    elif mainCategory == "Fashion":
        model = model_list[5]
    elif mainCategory == "Games":
        model = model_list[6]
    elif mainCategory == "Theater":
        model = model_list[7]
    elif mainCategory == "Music":
        model = model_list[8]
    elif mainCategory == "Crafts":
        model = model_list[9]  
    elif mainCategory == "Technology":
        model = model_list[10]
    elif mainCategory == "Comics":
        model = model_list[11]
    print(mainCategory)

###-----MODEL PREDICTION-----###
    pred = model.predict(my_data)
    print(pred[0])

    success = int(pred[0])
    result = {'success' : success}
    result = json.dumps(result)
    return(result)


if __name__ == '__main__':
    app.run(debug=True)

