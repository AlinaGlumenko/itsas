import os
import pandas as pd


def getDataFromFile(path, columnsNames):
    data = pd.read_excel(path)
    df = pd.DataFrame(data, columns = columnsNames)
    # df = pd.DataFrame(data, columns = ['Letter frequency', \
                                        # 'Numbers frequency', \
                                        # 'Signs frequency', \
                                        # 'Data volume', \
                                        # 'Search ability', \
                                        # 'Presence of meaning', \
                                        # 'Format', \
                                        # 'Shelf life', \
                                        # 'Result'])
    
    df.head()
    return df