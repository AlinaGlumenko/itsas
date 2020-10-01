import os
import pandas as pd


def getDataFromFile(path, columnsNames):
    data = pd.read_excel(path)
    df = pd.DataFrame(data, columns = columnsNames)    
    return df
