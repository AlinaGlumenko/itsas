import os
from flask import Flask, render_template, request, redirect, send_file
from logic.classifier import buildClassifier, startClassify
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

app.config["RESULT_VALUES"] = ['garbage', 'NoSQL key-value - cache', \
                                'NoSQL column - users', 'NoSQL document - courses', \
                                'SQL - finance']


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
                buildClassifier(app.config["TRAINING_DATA_PATH"], 'custom', testSize, app.config["COLUMN_NAMES"])                                       
        else:
            # build default classifier
            buildClassifier(app.config["TRAINING_DATA_PATH"], 'default', testSize, app.config["COLUMN_NAMES"])
            
        return redirect('/confusion_matrix')
    return render_template('classifier.html')


@app.route('/confusion_matrix', methods=["GET", "POST"])
def confusionMatrix():
    # посчитать точность для обучающей выборки, учитывая выбранный файл (дефолтный или кастомный)
    # посчитать точность для тестовой выборки, учитывая выбранный файл (дефолтный или кастомный)
    

    # classes = ['Cannot detect', 'Citroen', 'Honda', 'Mercedes', 'Opel', 'Renault']
    # elements = RecognitionManager().recognize_images(app.config["IMAGES_TEST"])
    # y_predicted = [el[1] for el in elements]
    # y_target = ImageManager().get_image_names(app.config["IMAGES_TEST"], classes[1:])
    # cm = RecognitionManager().get_confusion_matrix(y_target, y_predicted)
    # accuracy = RecognitionManager().get_accuracy(y_target, y_predicted)
    # return render_template('confusion_matrix.html', matrix=cm, classes=classes, accuracy=accuracy)
    return render_template('confusion_matrix.html')


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
                filenameWithResults = startClassify(app.config["USING_DATA_PATH"], app.config["COLUMN_NAMES"][-1])
                # allow to user download file with Results
                filePath = app.config["DOWNLOAD_PATH"] + filenameWithFeatures
                return send_file(filePath)
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
                return send_file(filePath)

        return redirect(request.url)
    return render_template('exploitation.html')


if __name__ == '__main__':
    app.run()