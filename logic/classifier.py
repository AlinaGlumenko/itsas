import os
import pickle
import pandas as pd
import numpy as np
from logic.fileManager import getFileByName
from logic.contentManager import getDataFromFile

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


def buildClassifier(path, choice, testSize, columnsNames, resultColNames):
    if choice == "custom":
        fullPath = getFileByName(path, "custom")
    else:
        fullPath = getFileByName(path, "default")
    
    data = getDataFromFile(fullPath, columnsNames)

    # print(data)
    getClassifierFor(data, testSize, columnsNames, resultColNames)


def getClassifierFor(data, testSize, columnsNames, resultColNames):
    testSize = int(testSize)

    data = data[[columnsNames[-1]] + columnsNames[:-1]]
    # del data[columnsNames[4]]
    print(data.columns)

    # prepare string data in cols (category) for training
    df_with_dummies = pd.get_dummies(data, columns=[columnsNames[3], columnsNames[4], columnsNames[5]])

    # create a dictionary with the label codification
    result_codes = {}
    for i, name  in enumerate(resultColNames):
        result_codes[name] = i
    
    # Category mapping
    df_with_dummies['Result_Code'] = df_with_dummies['Result']
    df_with_dummies = df_with_dummies.replace({'Result_Code': result_codes})
    
    X = df_with_dummies[list(df_with_dummies.columns)[1:-1]] # Features
    y = df_with_dummies['Result_Code']  # Labels
    
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize/100) # for example, 70% training and 30% test

    #Create a Gaussian Classifier
    # clf = RandomForestClassifier(n_estimators=100, random_state=3)
    clf = RandomForestClassifier(n_estimators=100)

    #Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Model Accuracy, how often is the classifier correct?
    accuracy = metrics.accuracy_score(y_test, y_pred)
    # print("Accuracy: ", accuracy)

    # save Classifier
    pathForRFSaving = os.getcwd() + "\\logic\\intermediateFiles\\"
    objForSaving = {
        'clf': clf,
        'featureNames': X.columns
    }
    with open(pathForRFSaving + 'db_rfc.pickle', 'wb') as output:
        pickle.dump(objForSaving, output)

    # get info for confusion matrix
    y_predicted_train = clf.predict(X_train)
    accuracy_train = metrics.accuracy_score(y_train, y_predicted_train)

    # prepare data for saving
    # convert NumPy Array to List
    y_predicted_train = y_predicted_train.tolist()
    y_train = y_train.tolist()
    y_pred = y_pred.tolist()
    y_test = y_test.tolist()

    # float to int
    y_predicted_train = [str(int(el)) for el in y_predicted_train]
    y_train = [str(int(el)) for el in y_train]
    y_pred = [str(int(el)) for el in y_pred]
    y_test = [str(int(el)) for el in y_test]

    # list of ints to string
    y_predicted_train_str = '|'.join(y_predicted_train)
    y_train_str = '|'.join(y_train)
    y_pred_str = '|'.join(y_pred)
    y_test_str = '|'.join(y_test)

    for k, v in result_codes.items():
        v = str(v)
        y_predicted_train_str = y_predicted_train_str.replace(v, k)
        y_train_str = y_train_str.replace(v, k)
        y_pred_str = y_pred_str.replace(v, k)
        y_test_str = y_test_str.replace(v, k)

    # print("accuracy_train: ", accuracy)
    obj = {
        'accuracy_train': accuracy_train,
        'accuracy_test': accuracy,
        'y_predicted_train': y_predicted_train_str.split("|"),
        'y_target_train': y_train_str.split("|"),
        'y_predicted_test': y_pred_str.split("|"),
        'y_target_test': y_test_str.split("|")
    }

    # save results for confusion matrix
    with open(pathForRFSaving + 'conf_matrix.pickle', 'wb') as output:
        pickle.dump(obj, output)


def startClassify(fullPath, columnsNames, resultColNames, dirPathForSaving):
    # load file with data as df by path
    data = getDataFromFile(fullPath, columnsNames[:-1].insert(0, 'Filename'))

    # prepare data
    preparedData = data[list(data.columns)[1:-1]]
    # del preparedData[columnsNames[4]]
    df_with_dummies = pd.get_dummies(preparedData, columns=[columnsNames[3], columnsNames[4], columnsNames[5]])

    # load db rfc
    path_rfc_pickle = os.getcwd() + "\\logic\\intermediateFiles\\db_rfc.pickle"
    with open(path_rfc_pickle, 'rb') as d:
        obj = pickle.load(d)
    
    featureNames = obj['featureNames']
    dbRfcModel = obj['clf']

    # fix the difference in columns
    nrows = len(data)
    diffs = list(set(featureNames) - set(df_with_dummies.columns))
    for diff in diffs:
        arr = [0 for row in range(0, nrows)]
        df_with_dummies[diff] = arr

    # rfc predict
    predictionRfc = dbRfcModel.predict(df_with_dummies)

    # decode output
    # create a dictionary with the label codification
    result_codes = {}
    for i, name  in enumerate(resultColNames):
        result_codes[name] = i

    # convert NumPy Array to List
    predictionRfc = predictionRfc.tolist()

    # float to int
    predictionRfc = [str(int(el)) for el in predictionRfc]

    # list of ints to string
    predictionRfc_str = '|'.join(predictionRfc)

    for k, v in result_codes.items():
        v = str(v)
        predictionRfc_str = predictionRfc_str.replace(v, k)

    result = predictionRfc_str.split("|")

    # add result column to data df
    data[columnsNames[-1]] = result

    # save to file for user
    filename = 'results.xlsx'
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(dirPathForSaving + filename, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    data.to_excel(writer, sheet_name='Sheet1', index=False)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return filename


def getConfusionMatrix(y_true, y_pred):
    '''calculate confusion matrix'''
    # Compute confusion matrix
    cm = metrics.confusion_matrix(y_true, y_pred)
    np.set_printoptions(precision=2)
    np.seterr(divide='ignore', invalid='ignore')
    cm = np.nan_to_num(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis])
    matrix = [[round(elem, 2) for elem in row] for row in cm]
    # print(matrix)
    return matrix

