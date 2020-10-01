import os
import pandas as pd


columnsNames = ['Filename', \
                'Letter frequency', 'Numbers frequency', \
                'Signs frequency', 'Сategory', \
                'File extension', 'Content Type', 'Result']

resultNames = ['garbage', \
                'NoSQL key-value - cache', \
                'NoSQL column - users', \
                'NoSQL document - courses', \
                'NoSQL key-value - support']


path = os.getcwd() + "\\exploitation.xlsx"

data = pd.read_excel(path)
df = pd.DataFrame(data, columns = columnsNames[:-1])

arr = []

nrows = len(df)
for row in range(0, nrows):
    category = df.loc[row]['Сategory']
    contentType = df.loc[row]['Content Type']
    fileExtension = df.loc[row]['File extension']

    if fileExtension == contentType:
        if (category == 'info' and contentType == 'html'):
            arr.append(resultNames[1])
        elif category == 'user' and contentType == 'txt':
            arr.append(resultNames[2])
        elif category == 'info' and contentType in ('xml', 'json', 'txt'):
            arr.append(resultNames[3])
        elif category == 'support' and contentType in ('xml', 'json'):
            arr.append(resultNames[4])
        else:
            arr.append(resultNames[0])
    else:
        arr.append(resultNames[0])

df["Result"] = arr

dirPathForSaving = os.getcwd() + "\\"
filename = 'trainingData.xlsx'

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(dirPathForSaving + filename, engine='xlsxwriter')
# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1', index=False)
# Close the Pandas Excel writer and output the Excel file.
writer.save()