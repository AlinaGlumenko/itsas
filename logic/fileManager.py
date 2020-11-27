import os


def allowedFile(filename, allowedExtensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowedExtensions


def secureCustomFilename(filename):
    newFilename = "custom." + filename.rsplit('.', 1)[1]
    return newFilename


def getFileByName(path, expectedName):
    '''get file by name from the directory'''        
    with os.scandir(path) as entries:
        for i, entry in enumerate(entries):
            resName = entry.name.rsplit(".", 1)[0]
            if entry.is_file() and expectedName == resName:                    
                return path + entry.name
    return ''


def saveRawDataFiles(files, filesDirPath, allowedExtensions):
    '''save files to directory'''             
    for file in files:            
        if allowedFile(file.filename, allowedExtensions):
            ext = file.filename.rsplit(".", 1)[1]
            file.save(os.path.join(filesDirPath, 
                                    "file" + str(getFilesCount(filesDirPath)) + "." + ext))
        else:
            print("can't save file")


def clearDir(filesDirPath, exceptionName=''):
    '''remove files from directory'''
    with os.scandir(filesDirPath) as entries:
        for entry in entries:
            name = entry.name.rsplit(".", 1)[0]
            if entry.is_file() and name != exceptionName:                    
                os.remove(filesDirPath + entry.name)


def getFilesCount(filesDirPath):
    '''get files count in the directory'''
    count = 0
    with os.scandir(filesDirPath) as entries:
        for entry in entries:
            if entry.is_file():                    
                count += 1
    return count