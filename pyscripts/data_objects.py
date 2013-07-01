#!/usr/bin/env python

import math
import numpy
from datetime import datetime
import string
import re
from curses.ascii import isdigit
import nltk
from nltk.corpus import cmudict
from nltk.tag.simplify import simplify_wsj_tag
from collections import Counter
import pdb
d = cmudict.dict()

STOP_WORDS = ['a','able','about','across','after','all','almost','also','am','among','an','and','any','are','as','at', \
              'be','because','been','but','by','can','cannot','could','dear','did','do','does','either','else','ever',\
              'every','for','from','get','got','had','has','have','he','her','hers','him','his','how','however','i','if',\
              'in','into','is','it','its','just','least','let','like','likely','may','me','might','most','must','my','neither',\
              'no','nor','not','of','off','often','on','only','or','other','our','own','rather','said','say','says','she','should',\
              'since','so','some','than','that','the','their','them','then','there','these','they','this','tis','to','too','twas',\
              'us','wants','was','we','were','what','when','where','which','while','who','whom','why','will','with','would','yet',\
              'you','your']

class ReviewText(object):
    def __init__(self, text, posAnalysis=None, readabilityAnalysis=None):
        self.rawText = text
        self.processedText = self.preprocessText(text)
        self.ncharacters = len(self.processedText.translate(string.maketrans("", ""), string.punctuation).replace(' ', ''))
        self.nwords = len(self.processedText.split())
        self.nsentences = self.nsent(self.processedText)
        self.npunctuation = len([x for x in self.rawText if x in string.punctuation])
        self.containsClosed = 1 if self.processedText.find('closed') >= 0 else 0
        self.nverbs = 0
        self.nnouns = 0
        self.nadjadv = 0
        self.nsyllables = 0
        self.npolysyllables = 0
        self.ari = 0
        self.fk = 0
        self.smog = 0

        # analyze text
        if posAnalysis is None:
            posAnalysis = True
        if readabilityAnalysis is None:
            readabilityAnalysis = True
        if posAnalysis:
            self.analyzePosAndSyllables(self.processedText)
        if readabilityAnalysis:
            self.analyzeReadability(self.processedText)

    def preprocessText(self, text):
        # remove quotation marks
        text = text.replace('\"', ' ')
        # deal with PS, p.s., p. s.
        text = re.sub('p\.s\.', 'ps', text)
        text = re.sub('p\. s\.', 'ps', text)
        # remove repeated spaces
        text = re.sub(' +', ' ', text)
        # remove spaces before punctuation/newline
        text = re.sub(' \n', '\n', text)
        text = re.sub(' \.', '.', text)
        text = re.sub(' ,', ',', text)
        text = re.sub(' !', '!', text)
        text = re.sub(' \?', '?', text)
        # remove repeated newlines
        text = re.sub('\n+', '\n', text)
        # remove newlines
        text = re.sub('\.\n', '. ', text)
        text = re.sub('!\n', '! ', text)
        text = re.sub(':\n', ': ', text)
        text = re.sub('\?\n', '? ', text)
        text = text.replace('\n', '.')
        # remove digits eg 1., 2., and special characters
        text = re.sub('[0-9]\.', ' ', text)
        text = text.replace('-', ' ')
        text = text.replace('*', ' ')
        # remove repeated puntuation
        text = re.sub('\.+', '. ', text)
        text = re.sub('!+', '! ', text)
        text = re.sub('\?+', '? ', text)
        # remove repeated spaces
        text = re.sub(' +', ' ', text)
        text = text.encode('ascii', 'ignore').lower().strip()
        return text

    def nsent(self, text):
        if len(text) == 0:
            return 0
        terminators = ['.', '!', '?']
        text = text.replace(' ', '')
        nsentences = len([x for x in text if x in terminators])
        if text[-1] not in terminators:
            nsentences = nsentences + 1
        return nsentences

    def nsyl(self, word):
        if word in d:
            return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word]]
        else:
            return [-1]

    def analyzePosAndSyllables(self, text):
        tags = nltk.pos_tag(nltk.word_tokenize(text))
        tags = [(word, simplify_wsj_tag(tag)) for word, tag in tags]
        adjadvtag = ['ADJ', 'ADV']
        verbtag = ['V', 'VD', 'VG', 'VN'] # leaving out modal verbs MOD
        nountag = ['N', 'NP'] # leaving out pronouns PRO
        for p in tags:
            syl = self.nsyl(p[0])[0]
            if p[1] in adjadvtag:
                self.nadjadv = self.nadjadv + 1
            if p[1] in verbtag:
                self.nverbs = self.nverbs + 1
            if p[1] in nountag:
                self.nnouns = self.nnouns + 1
            if syl > 0:
                self.nsyllables = self.nsyllables + 1
            if syl >= 3:
                self.npolysyllables = self.npolysyllables + 1

    def analyzeReadability(self, text):
        if self.nsentences > 0 and self.nwords > 0:
            self.ari = 4.71*(float(self.ncharacters)/float(self.nwords)) + .5*(float(self.nwords)/float(self.nsentences)) - 21.43
            self.fk = 0.39*(float(self.nwords)/float(self.nsentences)) + 11.8*(float(self.nsyllables)/float(self.nwords)) - 15.59
            self.smog = 1.0430*math.sqrt(float(self.npolysyllables)*(30.0/float(self.nsentences))) + 3.1291

class Review(object):
    def __init__(self, jsonData, businessCategories, today, posAnalysis=None, readabilityAnalysis=None):
        self.reviewId = jsonData['review_id']
        self.userId = jsonData['user_id']
        self.businessId = jsonData['business_id']
        self.businessCategory = businessCategories[jsonData['business_id']]
        self.stars = float(jsonData['stars'])
        self.age = (today - datetime.strptime(jsonData['date'], '%Y-%m-%d')).days
        self.funny = int(jsonData['votes']['funny']) if 'votes' in jsonData else None
        self.useful = int(jsonData['votes']['useful']) if 'votes' in jsonData else None
        self.cool = int(jsonData['votes']['cool']) if 'votes' in jsonData else None
        if posAnalysis is None:
            posAnalysis = True
        if readabilityAnalysis is None:
            readabilityAnalysis = True
        self.reviewText = ReviewText(jsonData['text'], posAnalysis, readabilityAnalysis)

class UserProfile(object):
    def __init__(self, jsonData):
        self.funny = int(jsonData['votes']['funny']) if 'votes' in jsonData else None
        self.useful = int(jsonData['votes']['useful']) if 'votes' in jsonData else None
        self.cool = int(jsonData['votes']['cool']) if 'votes' in jsonData else None
        self.averageStars = float(jsonData['average_stars'])
        self.reviewCount = int(jsonData['review_count'])

class User(object):
    def __init__(self, userId, jsonUserDict, reviewDict):
        # jsonUserDict is userId->json user data dictionary; reviewDict is userId->[Review] dictionary
        self.userId = userId
        self.profile = UserProfile(jsonUserDict[userId]) if userId in jsonUserDict else None
        self.reviews = { }
        if userId in reviewDict:
            for review in reviewDict[userId]:
                self.reviews[review.reviewId] = review

class BusinessProfile(object):
    def __init__(self, category, jsonData):
        self.closed = 0 if jsonData['open'] == True else 1
        self.stars = float(jsonData['stars'])
        self.reviewCount = int(jsonData['review_count'])
        self.category = category

class Business(object):
    def __init__(self, businessId, category, jsonBusinessDict, reviewDict):
        # jsonBusinessDict is businessId->json business data dictionary; reviewDict is businessId->[Review] dictionary
        self.businessId = businessId
        self.profile = BusinessProfile(category, jsonBusinessDict[businessId]) if businessId in jsonBusinessDict else None
        self.reviews = { }
        if businessId in reviewDict:
            for review in reviewDict[businessId]:
                self.reviews[review.reviewId] = review

class ReviewFeatures(object):
    header = ['logUsefulVotes', 'userId', 'businessId', 'userIsPublic', 'userHasVotes', 'userHasManySampleReviews', \
              'businessHasProfile', 'businessHasManyReviews', 'businessHasManySampleReviews', 'numUserReviews', \
              'numUserSampleReviews', 'numBusinessReviews', 'numBusinessSampleReviews', 'numUserSampleReviewsInCategory', \
              'reviewIsModerate', 'reviewStars', 'userStarsSd', 'reviewVsUserAvg', 'reviewVsUserAvgNormalized', \
              'businessStarsSd', 'reviewVsBusinessAvg', 'reviewVsBusinessAvgNormalized', 'reviewAge', 'reviewCharacters', \
              'reviewWords', 'reviewSentences', 'reviewWordsPerSentence', 'reviewPunctuationPerSentence', 'reviewContainsClosed', \
              'reviewAdjectivesAndAdverbs', 'reviewVerbs', 'reviewNouns', 'reviewAdjectivesAndAdverbsPerWord', 'reviewVerbsPerWord', \
              'reviewNounsPerWord', 'reviewARI', 'reviewFK', 'reviewSMOG', 'earliestReview', 'funnyProfileVotesPerReview', \
              'usefulProfileVotesPerReview', 'coolProfileVotesPerReview', 'funnyProfileVotesPerReviewPerDay', \
              'usefulProfileVotesPerReviewPerDay', 'coolProfileVotesPerReviewPerDay', 'funnyVotesPerReview', 'usefulVotesPerReview', \
              'coolVotesPerReview', 'funnyVotesPerReviewPerDay', 'usefulVotesPerReviewPerDay', 'coolVotesPerReviewPerDay', \
              'userCharactersPerReview', 'userARI', 'userFK', 'userSMOG', 'businessClosed', 'earliestBusinessReview', \
              'businessCharactersPerReview', 'businessARI', 'businessFK', 'businessSMOG', 'similarityToOtherReviews', 'category']

    def __init__(self, review, user, business):
        # other user reviews and business reviews
        userReviewSamples = [r for r in user.reviews.values() if r.reviewId != review.reviewId and r.useful is not None]
        businessReviewSamples = [r for r in business.reviews.values() if r.reviewId != review.reviewId]

        # target, ids
        self.logUsefulVotes = math.log(review.useful + 1) if review.useful >= 0 else -1
        self.userId = review.userId
        self.businessId = review.businessId

        # user/business profile/review availability
        self.userIsPublic = 1 if user.profile is not None else 0
        self.userHasVotes = 1 if (user.profile is not None and user.profile.useful is not None) else 0
        self.userHasManySampleReviews = 1 if len(userReviewSamples) >= 5 else 0
        self.businessHasProfile = 1 if business.profile is not None else 0
        self.businessHasManyReviews = 1 if (business.profile is not None and business.profile.reviewCount >= 15) else 0
        self.businessHasManySampleReviews = 1 if len(businessReviewSamples) >= 5 else 0

        # user/business review count
        self.numUserReviews = user.profile.reviewCount if user.profile is not None else 'NA' # profile if available
        self.numUserSampleReviews = len(userReviewSamples)
        self.numBusinessReviews = business.profile.reviewCount if business.profile is not None else 'NA' # profile if available
        self.numBusinessSampleReviews = len(businessReviewSamples)
        self.numUserSampleReviewsInCategory = len([r for r in userReviewSamples if r.businessCategory == business.profile.category])

        # stars, stars distribution, number of reviews
        userStars = numpy.array([r.stars for r in userReviewSamples])
        businessStars = numpy.array([r.stars for r in businessReviewSamples])
        meanUserStars = user.profile.averageStars if user.profile is not None else (userStars.mean() if len(userStars) > 0 else 'NA')
        meanBusinessStars = business.profile.stars if business.profile is not None else (businessStars.mean() if len(businessStars) > 0 else 'NA')
        self.reviewStars = review.stars
        self.reviewIsModerate = 1 if review.stars == 3 else 0
        self.userStarsSd = numpy.sqrt((userStars**2).mean() - userStars.mean()**2) if len(userStars) > 1 else 'NA'
        self.reviewVsUserAvg = review.stars - meanUserStars if meanUserStars != 'NA' else 'NA'
        self.reviewVsUserAvgNormalized = float(self.reviewVsUserAvg)/self.userStarsSd if (len(userStars) > 1 and self.userStarsSd > 0) else 'NA'
        self.businessStarsSd = numpy.sqrt((businessStars**2).mean() - businessStars.mean()**2) if len(businessStars) > 1 else 'NA'
        self.reviewVsBusinessAvg = review.stars - meanBusinessStars if meanBusinessStars != 'NA' else 'NA'
        self.reviewVsBusinessAvgNormalized = float(self.reviewVsBusinessAvg)/self.businessStarsSd if (len(businessStars) > 1 and self.businessStarsSd > 0) else 'NA'

        # review age and text attributes
        self.reviewAge = review.age
        self.reviewCharacters = review.reviewText.ncharacters
        self.reviewWords = review.reviewText.nwords
        self.reviewSentences = review.reviewText.nsentences
        self.reviewWordsPerSentence = float(self.reviewWords)/float(self.reviewSentences) if self.reviewSentences > 0 else 0
        self.reviewPunctuationPerSentence = float(review.reviewText.npunctuation)/float(self.reviewSentences) if self.reviewSentences > 0 else 0
        self.reviewContainsClosed = review.reviewText.containsClosed
        self.reviewAdjectivesAndAdverbs = review.reviewText.nadjadv
        self.reviewVerbs = review.reviewText.nverbs
        self.reviewNouns = review.reviewText.nnouns
        self.reviewAdjectivesAndAdverbsPerWord = float(review.reviewText.nadjadv)/float(self.reviewWords) if self.reviewWords > 0 else 0
        self.reviewVerbsPerWord = float(review.reviewText.nverbs)/float(self.reviewWords) if self.reviewWords > 0 else 0
        self.reviewNounsPerWord = float(review.reviewText.nnouns)/float(self.reviewWords) if self.reviewWords > 0 else 0
        self.reviewARI = review.reviewText.ari
        self.reviewFK = review.reviewText.fk
        self.reviewSMOG = review.reviewText.smog

        # user attributes
        self.earliestReview = min([r.age for r in userReviewSamples]) if len(userReviewSamples) > 0 else 'NA'
        if (user.profile is not None and self.userHasVotes == 1 and self.numUserSampleReviews > 1):
            self.funnyProfileVotesPerReview = float(user.profile.funny)/self.numUserReviews
            self.usefulProfileVotesPerReview = float(user.profile.useful)/self.numUserReviews
            self.coolProfileVotesPerReview = float(user.profile.cool)/self.numUserReviews
            self.funnyProfileVotesPerReviewPerDay = self.funnyProfileVotesPerReview/self.earliestReview
            self.usefulProfileVotesPerReviewPerDay = self.usefulProfileVotesPerReview/self.earliestReview
            self.coolProfileVotesPerReviewPerDay = self.coolProfileVotesPerReview/self.earliestReview
            self.funnyVotesPerReview = float(sum([r.funny for r in userReviewSamples]))/len(userReviewSamples)
            self.usefulVotesPerReview = float(sum([r.useful for r in userReviewSamples]))/len(userReviewSamples)
            self.coolVotesPerReview = float(sum([r.cool for r in userReviewSamples]))/len(userReviewSamples)
            self.funnyVotesPerReviewPerDay = self.funnyVotesPerReview/self.earliestReview
            self.usefulVotesPerReviewPerDay = self.usefulVotesPerReview/self.earliestReview
            self.coolVotesPerReviewPerDay = self.coolVotesPerReview/self.earliestReview
        elif (user.profile is not None and self.userHasVotes == 1 and self.numUserSampleReviews <= 1):
            self.funnyProfileVotesPerReview = float(user.profile.funny)/self.numUserReviews
            self.usefulProfileVotesPerReview = float(user.profile.useful)/self.numUserReviews
            self.coolProfileVotesPerReview = float(user.profile.cool)/self.numUserReviews
            self.funnyProfileVotesPerReviewPerDay = 'NA'
            self.usefulProfileVotesPerReviewPerDay = 'NA'
            self.coolProfileVotesPerReviewPerDay = 'NA'
            self.funnyVotesPerReview = 'NA'
            self.usefulVotesPerReview = 'NA'
            self.coolVotesPerReview = 'NA'
            self.funnyVotesPerReviewPerDay = 'NA'
            self.usefulVotesPerReviewPerDay = 'NA'
            self.coolVotesPerReviewPerDay = 'NA'
        elif (self.userHasVotes == 0 and self.numUserSampleReviews > 0):
            self.funnyProfileVotesPerReview = 'NA'
            self.usefulProfileVotesPerReview = 'NA'
            self.coolProfileVotesPerReview = 'NA'
            self.funnyProfileVotesPerReviewPerDay = 'NA'
            self.usefulProfileVotesPerReviewPerDay = 'NA'
            self.coolProfileVotesPerReviewPerDay = 'NA'
            self.funnyVotesPerReview = float(sum([r.funny for r in userReviewSamples]))/len(userReviewSamples)
            self.usefulVotesPerReview = float(sum([r.useful for r in userReviewSamples]))/len(userReviewSamples)
            self.coolVotesPerReview = float(sum([r.cool for r in userReviewSamples]))/len(userReviewSamples)
            self.funnyVotesPerReviewPerDay = self.funnyVotesPerReview/self.earliestReview
            self.usefulVotesPerReviewPerDay = self.usefulVotesPerReview/self.earliestReview
            self.coolVotesPerReviewPerDay = self.coolVotesPerReview/self.earliestReview
        else:
            self.funnyProfileVotesPerReview = 'NA'
            self.usefulProfileVotesPerReview = 'NA'
            self.coolProfileVotesPerReview = 'NA'
            self.funnyProfileVotesPerReviewPerDay = 'NA'
            self.usefulProfileVotesPerReviewPerDay = 'NA'
            self.coolProfileVotesPerReviewPerDay = 'NA'
            self.funnyVotesPerReview = 'NA'
            self.usefulVotesPerReview = 'NA'
            self.coolVotesPerReview = 'NA'
            self.funnyVotesPerReviewPerDay = 'NA'
            self.usefulVotesPerReviewPerDay = 'NA'
            self.coolVotesPerReviewPerDay = 'NA'

        self.userCharactersPerReview = 0 # calculateUserTextFeatures
        self.userARI = 0 # calculateUserTextFeatures
        self.userFK = 0 # calculateUserTextFeatures
        self.userSMOG = 0 # calculateUserTextFeatures

        # business attributes
        self.businessClosed = business.profile.closed if business.profile is not None else 0
        self.earliestBusinessReview = min([r.age for r in businessReviewSamples]) if len(businessReviewSamples) > 0 else 'NA'
        self.businessCharactersPerReview = 0 # calculateBusinessTextFeatures
        self.businessARI = 0 # calculateBusinessTextFeatures
        self.businessFK = 0 # calculateBusinessTextFeatures
        self.businessSMOG = 0 # calculateBusinessTextFeatures
        self.similarityToOtherReviews = 0 # calculateBusinessTextFeatures
        self.category = review.businessCategory
       
        # calculate sample review features
        if self.numUserSampleReviews > 0:
            self.calculateUserTextFeatures(userReviewSamples, user)
        if self.numBusinessSampleReviews > 0:
            self.calculateBusinessTextFeatures(businessReviewSamples, business, review)

    def calculateUserTextFeatures(self, userReviewSamples, user):
        ncharacters = 0.0
        nwords = 0.0
        nsentences = 0.0
        nsyllables = 0.0
        npolysyllables = 0.0
        for userReview in userReviewSamples:
            ncharacters = ncharacters + userReview.reviewText.ncharacters
            nwords = nwords + userReview.reviewText.nwords
            nsentences = nsentences + userReview.reviewText.nsentences
            nsyllables = nsyllables + userReview.reviewText.nsyllables
            npolysyllables = npolysyllables + userReview.reviewText.npolysyllables

        self.userCharactersPerReview = float(ncharacters)/self.numUserSampleReviews
        if nwords > 0 and nsentences > 0:
            self.userARI = 4.71*(float(ncharacters)/nwords) + .5*(float(nwords)/nsentences) - 21.43
            self.userFK = 0.39*(float(nwords)/nsentences) + 11.8*(float(nsyllables)/nwords) - 15.59
            self.userSMOG = 1.0430*math.sqrt(npolysyllables*(30.0/nsentences)) + 3.1291

    def calculateBusinessTextFeatures(self, businessReviewSamples, business, review):
        terms = [c[0] for c in Counter(review.reviewText.processedText.split()).most_common() if c[0] not in STOP_WORDS]
        ncharacters = 0.0
        nwords = 0.0
        nsentences = 0.0
        nsyllables = 0.0
        npolysyllables = 0.0
        tf = [] # list of dictionaries (word -> frequency)
        df = dict(zip(terms, [0]*len(terms)))
        for businessReview in businessReviewSamples:
            ncharacters = ncharacters + businessReview.reviewText.ncharacters
            nwords = nwords + businessReview.reviewText.nwords
            nsentences = nsentences + businessReview.reviewText.nsentences
            nsyllables = nsyllables + businessReview.reviewText.nsyllables
            npolysyllables = npolysyllables + businessReview.reviewText.npolysyllables
            tf.append(dict(Counter(businessReview.reviewText.processedText.split()).most_common())) # term frequency
            for term in tf[-1].keys():
                if term in df:
                    df[term] = df[term] + 1

        # calculate similarity to other reviews for this business
        if len(terms) > 0:
            tfidfPerDocument = []
            for d in tf:
                tfidf = [0]*len(terms)
                for i in xrange(len(terms)):
                    tfidf[i] = math.log(1 + d[terms[i]]) * math.log(float(len(tf))/df[terms[i]]) if terms[i] in d else 0
                tfidfPerDocument.append(numpy.array(tfidf).mean())
            self.similarityToOtherReviews = numpy.array(tfidfPerDocument).mean()

        self.businessCharactersPerReview = float(ncharacters)/self.numBusinessSampleReviews
        if nwords > 0 and nsentences > 0:
            self.businessARI = 4.71*(float(ncharacters)/nwords) + .5*(float(nwords)/nsentences) - 21.43
            self.businessFK = 0.39*(float(nwords)/nsentences) + 11.8*(float(nsyllables)/nwords) - 15.59
            self.businessSMOG = 1.0430*math.sqrt(npolysyllables*(30.0/nsentences)) + 3.1291

    def getList(self):
        return [self.logUsefulVotes, \
                self.userId, \
                self.businessId, \
                self.userIsPublic, \
                self.userHasVotes, \
                self.userHasManySampleReviews, \
                self.businessHasProfile, \
                self.businessHasManyReviews, \
                self.businessHasManySampleReviews, \
                self.numUserReviews, \
                self.numUserSampleReviews, \
                self.numBusinessReviews, \
                self.numBusinessSampleReviews , \
                self.numUserSampleReviewsInCategory, \
                self.reviewIsModerate, \
                self.reviewStars, \
                self.userStarsSd, \
                self.reviewVsUserAvg, \
                self.reviewVsUserAvgNormalized, \
                self.businessStarsSd, \
                self.reviewVsBusinessAvg, \
                self.reviewVsBusinessAvgNormalized, \
                self.reviewAge, \
                self.reviewCharacters, \
                self.reviewWords, \
                self.reviewSentences, \
                self.reviewWordsPerSentence, \
                self.reviewPunctuationPerSentence, \
                self.reviewContainsClosed, \
                self.reviewAdjectivesAndAdverbs, \
                self.reviewVerbs, \
                self.reviewNouns, \
                self.reviewAdjectivesAndAdverbsPerWord, \
                self.reviewVerbsPerWord, \
                self.reviewNounsPerWord, \
                self.reviewARI, \
                self.reviewFK, \
                self.reviewSMOG, \
                self.earliestReview, \
                self.funnyProfileVotesPerReview, \
                self.usefulProfileVotesPerReview, \
                self.coolProfileVotesPerReview, \
                self.funnyProfileVotesPerReviewPerDay, \
                self.usefulProfileVotesPerReviewPerDay, \
                self.coolProfileVotesPerReviewPerDay, \
                self.funnyVotesPerReview, \
                self.usefulVotesPerReview, \
                self.coolVotesPerReview, \
                self.funnyVotesPerReviewPerDay, \
                self.usefulVotesPerReviewPerDay, \
                self.coolVotesPerReviewPerDay, \
                self.userCharactersPerReview, \
                self.userARI, \
                self.userFK, \
                self.userSMOG, \
                self.businessClosed, \
                self.earliestBusinessReview, \
                self.businessCharactersPerReview, \
                self.businessARI, \
                self.businessFK, \
                self.businessSMOG, \
                self.similarityToOtherReviews, \
                self.category]
