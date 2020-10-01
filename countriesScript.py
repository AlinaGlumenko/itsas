import os
import json


countriesPath = os.getcwd() + "\\logic\\intermediateFiles\\countriesDefault.json"
with open(countriesPath, "r") as f:
    countries = json.load(f)

countryDict = {}
for k, v in countries[0].items():
    arr = []
    for el in v['countries']:
        arr.append(el['country'])
    countryDict[k] = arr

countriesPath = os.getcwd() + "\\logic\\intermediateFiles\\countries.json"
with open(countriesPath, 'w') as fp:
    json.dump(countryDict, fp)