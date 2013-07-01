#!/usr/bin/env python

import json
from datetime import datetime
import csv
import random
from data_objects import *
import pdb

DATA_DIR = '../data/'
BUSINESS_CATEGORIES_FILENAME = DATA_DIR + 'business_clusters.csv'
TRAINING_REVIEW_FILENAME = DATA_DIR + 'training/json/yelp_training_set_review.json'
TEST_REVIEW_FILENAME = DATA_DIR + 'test/json/yelp_test_set_review.json'
TRAINING_USER_FILENAME = DATA_DIR + 'training/json/yelp_training_set_user.json'
TEST_USER_FILENAME = DATA_DIR + 'test/json/yelp_test_set_user.json'
TRAINING_BUSINESS_FILENAME = DATA_DIR + 'training/json/yelp_training_set_business.json'
TEST_BUSINESS_FILENAME = DATA_DIR + 'test/json/yelp_test_set_business.json'
TRAINING_OUTPUTFILE = DATA_DIR + 'training/training_features.csv'
TEST_OUTPUTFILE = DATA_DIR + 'test/test_features.csv'
TRAINING_DATE = datetime.strptime('2013-01-19', '%Y-%m-%d')
TEST_DATE = datetime.strptime('2013-03-12', '%Y-%m-%d')

def loadReviews(categories):
    f = open(TRAINING_REVIEW_FILENAME, 'r')
    trainingReviews = { }
    trainingReviewIds = [ ]
    i = 0
    for line in f:
        data = json.loads(line)
        trainingReviews[data['review_id']] = Review(data, categories, TRAINING_DATE)
        trainingReviewIds.append(data['review_id'])
        i = i + 1
    f.close()

    f = open(TEST_REVIEW_FILENAME, 'r')
    testReviews = { }
    testReviewIds = [ ]
    i = 0
    for line in f:
        data = json.loads(line)
        testReviews[data['review_id']] = Review(data, categories, TEST_DATE)
        testReviewIds.append(data['review_id'])
        i = i + 1
    f.close()

    return (trainingReviews, trainingReviewIds, testReviews, testReviewIds)

def loadUsers(reviews):
    # get all unique user IDs within reviews
    userIds = set([review.userId for review in reviews.values()])

    # load json data
    f = open(TRAINING_USER_FILENAME, 'r')
    jsonUserDict = { }
    for line in f:
        jsonData = json.loads(line)
        jsonUserDict[jsonData['user_id']] = jsonData
    f.close()

    f = open(TEST_USER_FILENAME, 'r')
    for line in f:
        jsonData = json.loads(line)
        jsonUserDict[jsonData['user_id']] = jsonData
    f.close()

    # get userId -> [Review] dictionary
    reviewDict = { }
    for review in reviews.values():
        if review.userId not in reviewDict:
            reviewDict[review.userId] = [ ]
        reviewDict[review.userId].append(review)

    # get dict of users
    users = { }
    for userId in userIds:
        users[userId] = User(userId, jsonUserDict, reviewDict)
        if (users[userId].profile is not None):
            if (random.random() < 0.3):
                users[userId].profile.funny = None
                users[userId].profile.useful = None
                users[userId].profile.cool = None

    return users

def loadBusinesses(reviews, categories):
    # get all unique business IDs within reviews
    businessIds = set([review.businessId for review in reviews.values()])

    # load json data
    f = open(TRAINING_BUSINESS_FILENAME, 'r')
    jsonBusinessDict = { }
    for line in f:
        jsonData = json.loads(line)
        jsonBusinessDict[jsonData['business_id']] = jsonData
    f.close()

    f = open(TEST_BUSINESS_FILENAME, 'r')
    for line in f:
        jsonData = json.loads(line)
        jsonBusinessDict[jsonData['business_id']] = jsonData
    f.close()

    # get businessId -> [Review] dictionary
    reviewDict = { }
    for review in reviews.values():
        if review.businessId not in reviewDict:
            reviewDict[review.businessId] = [ ]
        reviewDict[review.businessId].append(review)

    # get dict of businesses
    businesses = { }
    for businessId in businessIds:
        businesses[businessId] = Business(businessId, categories[businessId], jsonBusinessDict, reviewDict)

    return businesses

def loadBusinessCategories():
    # load business category data
    categories = { }
    f = open(BUSINESS_CATEGORIES_FILENAME, 'r')
    csvReader = csv.reader(f, delimiter=',')
    header = True
    for row in csvReader:
        if header:
            header = False
            continue
        categories[row[0]] = int(row[1])
    f.close()
    return categories

def writeFeatures(reviewIds, reviews, users, businesses, filename):
    f = open(filename, 'wb')
    csvWriter = csv.writer(f, delimiter=',')
    csvWriter.writerow(ReviewFeatures.header)
    for reviewId in reviewIds:
        review = reviews[reviewId]
        features = ReviewFeatures(review, users[review.userId], businesses[review.businessId])
        csvWriter.writerow(features.getList())
    f.close()

def main():
    categories = loadBusinessCategories()
    (trainingReviews, trainingReviewIds, testReviews, testReviewIds) = loadReviews(categories) # dictionary of review ID -> review
    allReviews = dict(trainingReviews.items() + testReviews.items())
    trainingUsers = loadUsers(trainingReviews) # dictionary of user ID -> user
    testUsers = loadUsers(allReviews) # dictionary of user ID -> user
    trainingBusinesses = loadBusinesses(trainingReviews, categories) # dictionary of business ID -> user
    testBusinesses = loadBusinesses(allReviews, categories) # dictionary of business ID -> user
    writeFeatures(trainingReviewIds, trainingReviews, trainingUsers, trainingBusinesses, TRAINING_OUTPUTFILE)
    writeFeatures(testReviewIds, testReviews, testUsers, testBusinesses, TEST_OUTPUTFILE)

if __name__ == '__main__':
    main()
