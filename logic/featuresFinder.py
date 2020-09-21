import os
import pandas as pd
import magic


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
            f = open(entry, "r")
            data = f.read()
            # get File extension
            fileExtension = filename[1]
            # get Letter frequency, Numbers frequency, Signs frequency
            letterFrequency, numbersFrequency, signsFrequency = getSymbolsFrequency(data)
            # get Content Type
            contentType = getContentType(os.path.join(rawDataDirPath, entry.name))
            # get Сategory
            category = getCategory(data)
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

# json, xml, text, html, unknown
def getContentType(filePath):
    if not os.path.exists(filePath):
        return 'unknown'
    contentType = magic.from_file(filePath, mime=True).lower()

    with open(filePath) as f:        
        if 'empty' in contentType:
            return 'empty'
        elif 'xml' in contentType:
            return 'xml'
        elif 'html' in contentType:
            return 'html'
        if 'json' in contentType or f.read(1) in '{[':
            return 'json'
        elif 'text' in contentType:
            return 'txt'
        else:
            return 'unknown'

# info, user, support, service, unknown
def getCategory(data):
    pass

# contains noise, clean
def getLabel(letterFrequency, category):
    if category in ('info', 'user', 'support', 'service') and letterFrequency < 0.5:
        return 'contains noise'
    else:
        return 'clean'


