import os
import pickle
from flask import Flask, render_template, request, redirect, send_file
from logic.classifier import buildClassifier, startClassify, getConfusionMatrix
from logic.fileManager import allowedFile, secureCustomFilename, saveRawDataFiles, clearDir
from logic.featuresFinder import findFeatures


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)


# configuration
app.config["DEBUG"] = True
app.config["DEFAULT_TRAINING_SET"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024
app.config["ALLOWED_SET_EXTENSIONS"] = ["xls", "xlsx", "xlsm"]
app.config["ALLOWED_RAW_DATA_EXTENSIONS"] = ["json", "txt", "html", "xml"]
app.config["RAW_DATA_PATH"] = app.root_path + "\\static\\sysfiles\\rawData\\"
app.config["TRAINING_DATA_PATH"] = app.root_path + "\\static\\sysfiles\\training\\"
app.config["USING_DATA_PATH"] = app.root_path + "\\static\\sysfiles\\using\\"
app.config["DOWNLOAD_PATH"] = app.root_path + "\\static\\sysfiles\\download\\"

app.config["COLUMN_NAMES"] = ['Letter frequency', 'Numbers frequency', \
                                'Signs frequency', 'Сategory', \
                                'File extension', 'Content Type', 'Result']

app.config["RESULT_VALUES"] = ['garbage', \
                                'NoSQL key-value - cache', \
                                'NoSQL column - users', \
                                'NoSQL document - courses', \
                                'NoSQL key-value - support']


@app.after_request
def addHeader(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def main():
    return redirect('/classifier')


@app.route('/classifier', methods=["GET", "POST"])
def classifier():
    if request.method == 'POST':
        # get test_size from form
        testSize = request.form.get('testSize')
        # check if testSize is numeric
        if not testSize.isnumeric():
            return redirect('/classifier')
        # get training set option
        selectTrainingSet = request.form.get('trainingSetSelect')
        # if custom
        if selectTrainingSet == 'custom':
            # get file with training set data
            trainingSetFile = request.files['trainingSetData']
            # check its fileanme
            if trainingSetFile.filename != '' and allowedFile(trainingSetFile.filename, app.config["ALLOWED_SET_EXTENSIONS"]):
                # flag for using custom training set file
                app.config["DEFAULT_TRAINING_SET"] = False
                # change filename
                filename = secureCustomFilename(trainingSetFile.filename)
                # clear dir
                clearDir(app.config['TRAINING_DATA_PATH'])
                # save file
                trainingSetFile.save(os.path.join(app.config['TRAINING_DATA_PATH'], filename))
                # build custom classifier
                buildClassifier(app.config["TRAINING_DATA_PATH"], 'custom', testSize, app.config["COLUMN_NAMES"], app.config["RESULT_VALUES"])                                       
        else:
            # build default classifier
            buildClassifier(app.config["TRAINING_DATA_PATH"], 'default', testSize, app.config["COLUMN_NAMES"], app.config["RESULT_VALUES"])
            
        # return redirect('/confusion_matrix')
        return redirect('/exploitation')

    return render_template('classifier.html')

import numpy as np
@app.route('/confusion_matrix', methods=["GET", "POST"])
def confusionMatrix():
    # load info for confusion matrix
    path_conf_matr_pickle = os.getcwd() + "\\logic\\intermediateFiles\\conf_matrix.pickle"
    with open(path_conf_matr_pickle, 'rb') as data:
        infoObj = pickle.load(data)
    
    if not infoObj:
        return redirect('/classifier')

    # get info for test set
    accuracy_test = infoObj['accuracy_test']
    y_predicted_test = infoObj['y_predicted_test']
    y_target_test = infoObj['y_target_test']

    # get confusion matrix for test
    cm_test = getConfusionMatrix(y_target_test, y_predicted_test)

    # get info for train set
    accuracy_train = infoObj['accuracy_train']
    y_predicted_train = infoObj['y_predicted_train']
    y_target_train = infoObj['y_target_train']

    # get confusion matrix for train
    cm_train = getConfusionMatrix(y_target_train, y_predicted_train)

    # classes
    classes = ['garbage', \
                'NoSQL key-value cache', \
                'NoSQL column users', \
                'NoSQL document courses', \
                'NoSQL key-value support']
    return render_template('confusion_matrix.html', classes=classes, \
                                                    matrixTrain=cm_train, accuracyTrain=accuracy_train, \
                                                    matrixTest=cm_test, accuracyTest=accuracy_test)


@app.route('/exploitation', methods=["GET", "POST"])
def exploitation():
    if request.method == 'POST':         
        form_name = request.form['form-name']
        if form_name == 'classification-form':
            exploitationSetData = request.files['exploitationSetData']
            if exploitationSetData.filename != '' and allowedFile(exploitationSetData.filename, app.config["ALLOWED_SET_EXTENSIONS"]):
                # change filename
                filename = secureCustomFilename(exploitationSetData.filename)
                # clear dir
                clearDir(app.config["USING_DATA_PATH"])
                # save file
                exploitationSetData.save(os.path.join(app.config["USING_DATA_PATH"], filename))
                # use classifier
                filenameWithResults = startClassify(os.path.join(app.config["USING_DATA_PATH"], filename), \
                                                    app.config["COLUMN_NAMES"], app.config["RESULT_VALUES"], \
                                                    app.config["DOWNLOAD_PATH"])
                # allow to user download file with Results
                filePath = app.config["DOWNLOAD_PATH"] + filenameWithResults
                return send_file(filePath, attachment_filename=filenameWithResults)
        else:
            rawDataFiles = request.files.getlist('rawData')
            if rawDataFiles:
                # clear dir
                clearDir(app.config["RAW_DATA_PATH"])
                # save files with raw data
                saveRawDataFiles(rawDataFiles, app.config["RAW_DATA_PATH"], app.config["ALLOWED_RAW_DATA_EXTENSIONS"])
                # create file with Features
                filenameWithFeatures = findFeatures(app.config["RAW_DATA_PATH"], app.config["DOWNLOAD_PATH"], app.config["COLUMN_NAMES"][:-1])
                # allow to user download file with Features
                filePath = app.config["DOWNLOAD_PATH"] + filenameWithFeatures
                return send_file(filePath, attachment_filename=filenameWithFeatures)

        return redirect(request.url)
    return render_template('exploitation.html')


if __name__ == '__main__':
    app.run()