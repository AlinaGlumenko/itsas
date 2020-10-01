import os
import re
import json 
import pandas as pd
import codecs
import magic
from names_dataset import NameDataset
from nltk.corpus import stopwords
# from country_list import countries_for_language
from logic.textCategorizer import categorize


def findFeatures(rawDataDirPath, dirPathForSaving, columnNames):
    filenameColumnName = 'Filename'
    labelColumnName = 'Label'
    filenameWithFeatures = 'features.xlsx'
    filenamesArr = []
    fileExtensionArr = []
    letterFrequencyArr = []
    numbersFrequencyArr = []
    signsFrequencyArr = []
    labelArr = []
    categoryArr = []
    contentTypeArr = []

    # find Features
    with os.scandir(rawDataDirPath) as entries:
        for entry in entries:
            filename = entry.name.rsplit(".", 1)

            f = codecs.open(entry, "r", "utf_8_sig")
            # f = open(entry, "r")
            # print(entry.name)

            data = f.read()
            # get File extension
            fileExtension = filename[1]
            # get Letter frequency, Numbers frequency, Signs frequency
            letterFrequency, numbersFrequency, signsFrequency = getSymbolsFrequency(data)
            # get Content Type
            contentType = getContentType(os.path.join(rawDataDirPath, entry.name))
            # get Сategory
            category = getCategory(data, contentType)
            # get Label
            label = getLabel(letterFrequency, category)

            # save Features to arrs
            filenamesArr.append(entry.name)
            letterFrequencyArr.append(letterFrequency)
            numbersFrequencyArr.append(numbersFrequency)
            signsFrequencyArr.append(signsFrequency)
            categoryArr.append(category)
            fileExtensionArr.append(fileExtension)
            contentTypeArr.append(contentType)
            labelArr.append(label)

    # create excel file
    # make dataframe from arrs with pd
    df = pd.DataFrame({filenameColumnName: filenamesArr,
                        columnNames[0]: letterFrequencyArr,
                        columnNames[1]: numbersFrequencyArr,
                        columnNames[2]: signsFrequencyArr,
                        columnNames[3]: categoryArr,
                        columnNames[4]: fileExtensionArr,
                        columnNames[5]: contentTypeArr,
                        labelColumnName: labelArr})
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(dirPathForSaving+filenameWithFeatures, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return filenameWithFeatures


def getSymbolsFrequency(s):
    if len(s) == 0:
        return 0, 0, 0
    numbers = sum(c.isdigit() for c in s)
    letters = sum(c.isalpha() for c in s)
    signs = len(s) - numbers - letters

    numbersFrequency = numbers/len(s)
    letterFrequency = letters/len(s)
    signsFrequency = signs/len(s)
    
    return letterFrequency, numbersFrequency, signsFrequency


# contains noise, clean
def getLabel(letterFrequency, category):
    if category in ('info', 'user', 'support') and letterFrequency < 0.7:
        return 'contains noise'
    else:
        return 'clean'


# json, xml, text, html, unknown
def getContentType(filePath):
    if not os.path.exists(filePath):
        return 'unknown'
    contentType = magic.from_file(filePath, mime=True).lower()

    with codecs.open(filePath, "r", "utf_8_sig" ) as f:
        dataFromFile = f.read()
    
    if 'empty' in contentType:
        return 'empty'
    elif 'xml' in contentType or "<root>" in dataFromFile and "</root>" in dataFromFile:
        return 'xml'
    elif 'html' in contentType:
        return 'html'
    elif 'json' in contentType or dataFromFile[0] in '{[':
        return 'json'
    elif 'text' in contentType:
        return 'txt'
    else:
        return 'unknown'


# regular expression for validating an Email
regex = '[^@]+@[^@]+\.[^@]+'
# function for validating an Email
def checkIsEmail(email):
    arr = email.strip().split(" ")
    if len(arr) > 1:
        return False
    
    if(re.search(regex, email)):  
        return True
    else:  
        return False


# country dict
countriesPath = os.getcwd() + "\\logic\\intermediateFiles\\countries.json"
with open(countriesPath, "r") as f:
    countries = json.load(f)
# function for checking an Location
def checkIsLocation(data):
    arr = data.strip().split(" ")
    if len(arr) > 5:
        return False

    if data[0] in countries.keys():
        countriesList = countries[data[0]]
    else:
        return False

    if len(data) == 1 and data.capitalize() in countriesList:
        return True

    for el in arr:
        if el.capitalize() in countriesList:
            return True
        else:
            for countryName in countriesList:
                arrOfCountryNameWords = countryName.split(' ')
                for word in arrOfCountryNameWords:
                    if el == word:
                        return True

    return False


# firstnames and lastnames
m = NameDataset()
# stop_words
stopWords = list(stopwords.words('english'))
# function for checking an Name
def checkIsName(data):
    arr = data.split(" ")
    if len(arr) > 5:
        return False

    flagFirstname, flagLastname = False, False
    for el in arr:
        if el in stopWords:  
            return False

        # to lower
        if m.search_first_name(el.capitalize()):
            flagFirstname = True
        
        if m.search_last_name(el.capitalize()):
            flagLastname = True 
    
    if flagFirstname or flagLastname:
        return True
    else: 
        return False


# info, user, support unknown
def getCategory(data, contentType):
    if data:
        # check if it is user data (firstname, lastname, email, location)
        if checkIsEmail(data) or checkIsName(data) or checkIsLocation(data):
            return 'user'
        else:
            # check if it is info or support
            category = categorize(data, contentType)
            return category
    return 'unknown'

