import os
import re
import pickle
import pandas as pd
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import punkt
from boilerpy3 import extractors
import xml.etree.ElementTree as ET
from nltk.corpus.reader import wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer


currPath = os.getcwd() + "\\logic\\intermediateFiles\\"

# load rfc
pathRfc = currPath + "best_rfc.pickle"
with open(pathRfc, 'rb') as data:
    rfcModel = pickle.load(data)

# TF-IDF object
pathTfidf = currPath + "tfidf.pickle"
with open(pathTfidf, 'rb') as data:
    tfidf = pickle.load(data)

# Category mapping dictionary
categoryCodes = {
    'info': 0,
    'support': 1,
    'unknown': 2
}

# get the category given the category code
def getCategoryName(categoryId):
    for category, id_ in categoryCodes.items():    
        if id_ == categoryId:
            return category


# get clean text from data
def getCleanText(data, contentType):

    if contentType == 'xml':
        arr = []
        xmlstr = data.replace('&', '')
        root = ET.fromstring(xmlstr)                
        for item in list(root):
            arr.append(item.text.encode('utf8'))
        
        lenArr = [len(str(el)) for el in arr]
        content = arr[lenArr.index(max(lenArr))]
    
    elif contentType == 'txt':
        content = data

    elif contentType == 'json':
        arr = []
        data = data.replace('@', '')
        data = re.sub(r"(?m)^\s+", "", data)

        entryContent = json.loads(data)
        if type(entryContent) is list:
            arr.extend(entryContent)
        else:
            for key, value in entryContent.items():
                arr.append(value)
        
        lenArr = [len(str(el)) for el in arr]
        content = arr[lenArr.index(max(lenArr))]

    elif contentType == 'html':
        extractor = extractors.ArticleExtractor()
        content = extractor.get_content(data)

    else:
        content = ''

    return content


punctuationSigns = list("?:!.,;")
stopWords = list(stopwords.words('english'))
# Feature engineering workflow
def createFeaturesFromText(data, contentType):
    # get clean text from data
    text = getCleanText(data, contentType)

    # getting features
    df = pd.DataFrame(columns=['Content'])

    if type(text) == bytes:
        text = text.decode("utf-8")
    elif type(text) == dict:
        text = json.dumps(text)
    df.loc[0] = text
    
    # Special character cleaning
    # \r and \n
    df['Content_Parsed_1'] = df['Content'].apply(str).str.replace("\r", " ")
    df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace("\n", " ")
    df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace("    ", " ")
    # " when quoting text
    df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace('"', '')
    
    # Upcase/downcase
    # Lowercasing the text
    df['Content_Parsed_2'] = df['Content_Parsed_1'].str.lower()
    
    # Punctuation signs
    df['Content_Parsed_3'] = df['Content_Parsed_2']
    for punctSign in punctuationSigns:
        df['Content_Parsed_3'] = df['Content_Parsed_3'].str.replace(punctSign, '')

    # Possessive pronouns
    df['Content_Parsed_4'] = df['Content_Parsed_3'].str.replace("'s", "")
    df['Content_Parsed_4'] = df['Content_Parsed_4'].fillna("")

    # Stemming and Lemmatization
    # Saving the lemmatizer into an object
    wordnetLemmatizer = WordNetLemmatizer()

    # In order to lemmatize, we have to iterate through every word
    nrows = len(df)
    lemmatizedTextList = []

    for row in range(0, nrows):        
        # Create an empty list containing lemmatized words
        lemmatizedList = []        
        # Save the text and its words into an object
        text = df.loc[row]['Content_Parsed_4']
        # remove links
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        # remove numbers
        text = re.sub(r'[0-9]+', '', text)
        # remove tags in <>
        text = re.sub(r'<[^>]*>', '', text)
        # remove tags <style>...</style>
        text = re.sub(r'<style[^>]*>(.*?)<\/style>', '', text)
        # remove tags <script>...</script>
        text = re.sub(r'<script[^>]*>(.*?)<\/script>', '', text)
        text_words = text.split(" ")
        # Iterate through every word to lemmatize
        for word in text_words:
            lemmatizedList.append(wordnetLemmatizer.lemmatize(word, pos="v"))
        # Join the list
        lemmatizedText = " ".join(lemmatizedList)
        # Append to the list containing the texts
        lemmatizedTextList.append(lemmatizedText)

    df['Content_Parsed_5'] = lemmatizedTextList

    # Stop words
    # loop through all the stop words
    df['Content_Parsed_6'] = df['Content_Parsed_5']
    for stopWord in stopWords:
        regexStopword = r"\b" + stopWord + r"\b"
        df['Content_Parsed_6'] = df['Content_Parsed_6'].str.replace(regexStopword, '')

    # Useless words
    uselessWords = ['wwwskillsharecom', 'staticskillsharecom', 'https', \
                    'undefined', 'yahoocom', 'sender', 'time', 'sameas', \
                    'message', 'http', 'schemaorg', 'uploads', 'logo', \
                    'aolcom', 'video', 'assets', 'images', 'nundefined', \
                    'skillshare', '252undefined', 'image', 'user']

    for uselessWord in uselessWords:
        regexUselessword = r"\b" + uselessWord + r"\b"
        df['Content_Parsed_6'] = df['Content_Parsed_6'].str.replace(regexUselessword, '')
    
    df = df['Content_Parsed_6']
    # df = df.rename(columns={'Content_Parsed_6': 'Content_Parsed'})
    df = df.rename({'Content_Parsed_6': 'Content_Parsed'}, axis='columns')
    
    # TF-IDF
    features = tfidf.transform(df).toarray()    
    return features


def categorize(data, contentType):
    # Predict using the input model
    predictionRfc = rfcModel.predict(createFeaturesFromText(data, contentType))[0]    
    # Return result
    categoryRfc = getCategoryName(predictionRfc)
    return categoryRfc

