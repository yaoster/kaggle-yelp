#!/usr/bin/env python

import json
import csv
import pdb

TRAINING_DATA_DIR = '../data/training/'
TEST_DATA_DIR = '../data/test/'
TRAINING_BUSINESS_FILENAME = TRAINING_DATA_DIR + 'json/yelp_training_set_business.json'
TEST_BUSINESS_FILENAME = TEST_DATA_DIR + 'json/yelp_test_set_business.json'
OUTPUT_FILENAME = TRAINING_DATA_DIR + '../data/business_categories.csv'

def loadBusinessData():
    categories = set()
    jsonData = dict()
    f = open(TRAINING_BUSINESS_FILENAME, 'r')
    for line in f:
        data = json.loads(line)
        jsonData[data['business_id']] = data
        for c in data['categories']:
            categories.add(c)
    f.close()
    f = open(TEST_BUSINESS_FILENAME, 'r')
    for line in f:
        data = json.loads(line)
        jsonData[data['business_id']] = data
        for c in data['categories']:
            categories.add(c)
    f.close()

    return (jsonData, sorted(categories))

def writeCategories(jsonData, categories):
    f = open(OUTPUT_FILENAME, 'wb')
    csvWriter = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    csvWriter.writerow(['id'] + sorted(categories.keys()))
    for businessId, data in jsonData.iteritems():
        line = [0] * (len(categories) + 1)
        line[0] = businessId
        for c in data['categories']:
            line[categories[c]] = 1
        csvWriter.writerow(line)
    f.close()

def main():
    (jsonData, categories) = loadBusinessData()
    categories = dict(zip(categories, range(1, len(categories) + 1)))
    writeCategories(jsonData, categories)

if __name__ == '__main__':
    main()
