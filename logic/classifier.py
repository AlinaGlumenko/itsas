from logic.fileManager import getFileByName
from logic.contentManager import getDataFromFile

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


def buildClassifier(path, choice, testSize, columnsNames):
    if choice == "custom":
        fullPath = getFileByName(path, "custom")
    else:
        fullPath = getFileByName(path, "default")
    
    data = getDataFromFile(fullPath, columnsNames)

    print(data)

    getClassifierFor(data, testSize, columnsNames)


def getClassifierFor(data, testSize, columnsNames):
    X = data[columnsNames[:-1]]
    # X = data[['Letter frequency', 'Numbers frequency', \
    #         'Signs frequency', 'Data volume', \
    #         'Search ability', 'Presence of meaning', \
    #         'File extension', 'Shelf life']]  # Features
    y = data[columnsNames[-1]]  # Labels
    # y = data['Result']  # Labels
    
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize) # for example, 70% training and 30% test

    #Create a Gaussian Classifier
    clf = RandomForestClassifier(n_estimators=100)

    # save Classifier to global var ?????????????????? for future using

    #Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Model Accuracy, how often is the classifier correct?
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    # clf.predict([[3, 5, 4, 2]])


def startClassify(path, resultColumnName):
    pass


