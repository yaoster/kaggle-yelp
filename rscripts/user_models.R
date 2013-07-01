rm(list=ls(all=TRUE))
library(randomForest)
TRAINING_DATA <- '/home/yaoster/Data/src/devsandbox/kaggle/yelp_recruiting/data/training/training_features.csv'
TEST_DATA <- '/home/yaoster/Data/src/devsandbox/kaggle/yelp_recruiting/data/test/test_features.csv'
SAVE_DATE <- '2013-06-30'

load.data.matrix <- function(filename)
{
    # read data from file
    data <- read.table(filename, sep=',', header=T, as.is=T)
    ncategories <- max(data$category) - 1
    nsamples <- dim(data)[1]
    nfeatures <- dim(data)[2] - 1 # non-business category features

    # add category columns to data
    business.categories <- matrix(0, nsamples, ncategories)
    colnames(business.categories) <- rep('', ncategories)
    for (i in 1:ncategories) {
        colnames(business.categories)[i] <- paste('category', i, sep='')
        business.categories[which(data$category == i), i] <- 1
    }

    # last column of data is business category; fill in some NA values
    data <- data.frame(data[,1:nfeatures], data.frame(business.categories))
    data$businessHasProfile <- NULL
    data$userId <- NULL
    data$businessId <- NULL
    data$businessStarsSd[is.na(data$businessStarsSd)] <- 0
    data$earliestBusinessReview[is.na(data$earliestBusinessReview)] <- 0
    data$reviewVsBusinessAvgNormalized[is.na(data$reviewVsBusinessAvgNormalized)] <- 
        data$reviewVsBusinessAvg[is.na(data$reviewVsBusinessAvgNormalized)]
    data$reviewVsUserAvgNormalized[is.na(data$reviewVsUserAvgNormalized)] <- 
        data$reviewVsUserAvg[is.na(data$reviewVsUserAvgNormalized)]
    return(data)
}

features.novotes.nosamples <- function(data)
{
    data$userHasVotes <- NULL
    data$userHasManySampleReviews <- NULL
    data$numUserSampleReviews <- NULL
    data$numUserSampleReviewsInCategory <- NULL
    data$userStarsSd <- NULL
    data$reviewVsUserAvgNormalized <- NULL
    data$earliestReview <- NULL
    data$funnyProfileVotesPerReview <- NULL
    data$usefulProfileVotesPerReview <- NULL
    data$coolProfileVotesPerReview <- NULL
    data$funnyProfileVotesPerReviewPerDay <- NULL
    data$usefulProfileVotesPerReviewPerDay <- NULL
    data$coolProfileVotesPerReviewPerDay <- NULL
    data$funnyVotesPerReview <- NULL
    data$usefulVotesPerReview <- NULL
    data$coolVotesPerReview <- NULL
    data$funnyVotesPerReviewPerDay <- NULL
    data$usefulVotesPerReviewPerDay <- NULL
    data$coolVotesPerReviewPerDay <- NULL
    data$userCharactersPerReview <- NULL
    data$userARI <- NULL
    data$userFK <- NULL
    data$userSMOG <- NULL
    data$numUserReviews[data$userIsPublic == 0] <- 0
    data$reviewVsUserAvg[data$userIsPublic == 0] <- 0
    return(data)
}

features.votes.nosamples <- function(data)
{
    data$userIsPublic <- NULL
    data$userHasVotes <- NULL
    data$userHasManySampleReviews <- NULL
    data$numUserSampleReviews <- NULL
    data$numUserSampleReviewsInCategory <- NULL
    data$userStarsSd <- NULL
    data$reviewVsUserAvgNormalized <- NULL
    data$earliestReview <- NULL
    data$userCharactersPerReview <- NULL
    data$userARI <- NULL
    data$userFK <- NULL
    data$userSMOG <- NULL
    data$funnyProfileVotesPerReviewPerDay <- NULL
    data$usefulProfileVotesPerReviewPerDay <- NULL
    data$coolProfileVotesPerReviewPerDay <- NULL
    data$funnyVotesPerReview <- NULL
    data$usefulVotesPerReview <- NULL
    data$coolVotesPerReview <- NULL
    data$funnyVotesPerReviewPerDay <- NULL
    data$usefulVotesPerReviewPerDay <- NULL
    data$coolVotesPerReviewPerDay <- NULL
    return(data)
}

features.novotes.samples <- function(data)
{
    data$userHasVotes <- NULL
    data$funnyProfileVotesPerReview <- NULL
    data$usefulProfileVotesPerReview <- NULL
    data$coolProfileVotesPerReview <- NULL
    data$funnyProfileVotesPerReviewPerDay <- NULL
    data$usefulProfileVotesPerReviewPerDay <- NULL
    data$coolProfileVotesPerReviewPerDay <- NULL
    data$numUserReviews[is.na(data$numUserReviews)] <- 0
    return(data)
}

features.votes.samples <- function(data)
{
    data$userIsPublic <- NULL
    data$userHasVotes <- NULL
    return(data)
}

################
### TRAINING ###
################
############################################################################
### train model for users with no vote information and no sample reviews ###
############################################################################
data <- load.data.matrix(TRAINING_DATA)
data <- data[data$userHasVotes == 0 & data$numUserSampleReviews <= 1,]
data <- as.matrix(features.novotes.nosamples(data))
gc(); rf.novotes.nosamples <- randomForest(x=data[,2:dim(data)[2]], y=data[,1], 
                                           ntree=201, mtry=30, corr.bias=T, do.trace=T)
save(rf.novotes.nosamples, file=paste('rf_novotes_nosamples_', SAVE_DATE, '.Rdata', sep=''))
rm(data, rf.novotes.nosamples)

#########################################################################
### train model for users with vote information but no sample reviews ###
#########################################################################
data <- load.data.matrix(TRAINING_DATA)
data <- data[data$userHasVotes == 1 & data$numUserSampleReviews <= 1,]
data <- as.matrix(features.votes.nosamples(data))
gc(); rf.votes.nosamples <- randomForest(x=data[,2:dim(data)[2]], y=data[,1], 
                                         ntree=201, mtry=30, corr.bias=T, do.trace=T)
save(rf.votes.nosamples, file=paste('rf_votes_nosamples_', SAVE_DATE, '.Rdata', sep=''))
rm(data, rf.votes.nosamples)

##############################################################################
### train model for users with no vote information but with sample reviews ###
##############################################################################
data <- load.data.matrix(TRAINING_DATA)
data <- data[data$userHasVotes == 0 & data$numUserSampleReviews > 1,]
data <- as.matrix(features.novotes.samples(data))
gc(); rf.novotes.samples <- randomForest(x=data[,2:dim(data)[2]], y=data[,1], 
                                         ntree=201, mtry=40, corr.bias=T, do.trace=T)
save(rf.novotes.samples, file=paste('rf_novotes_samples_', SAVE_DATE, '.Rdata', sep=''))
rm(data, rf.novotes.samples)

######################################################################
### train model for users with vote information and review samples ###
######################################################################
data <- load.data.matrix(TRAINING_DATA)
data <- data[data$userHasVotes == 1 & data$numUserSampleReviews > 1,]
data <- as.matrix(features.votes.samples(data))
gc(); rf.votes.samples <- randomForest(x=data[,2:dim(data)[2]], y=data[,1], 
                                       ntree=125, mtry=40, corr.bias=T, do.trace=T)
save(rf.votes.samples, file=paste('rf_votes_samples_', SAVE_DATE, '.Rdata', sep=''))
rm(data, rf.votes.samples)

###############
### TESTING ###
###############
load(file=paste('rf_votes_samples_', SAVE_DATE, '.Rdata', sep=''))
load(file=paste('rf_votes_nosamples_', SAVE_DATE, '.Rdata', sep=''))
load(file=paste('rf_novotes_samples_', SAVE_DATE, '.Rdata', sep=''))
load(file=paste('rf_novotes_nosamples_', SAVE_DATE, '.Rdata', sep=''))
review.ids <- read.table('predicted_votes.csv', sep=',', header=T, as.is=T)$id
test.data <- load.data.matrix(TEST_DATA)
prediction <- rep(0, dim(test.data)[1])

############################################################
### users with no vote information and no sample reviews ###
############################################################
idx <- which(test.data$userHasVotes == 0 & test.data$numUserSampleReviews <= 1)
data <- as.matrix(features.novotes.nosamples(test.data[idx,]))
prediction[idx] <- predict(rf.novotes.nosamples, data[,2:dim(data)[2]])

#########################################################
### users with vote information but no sample reviews ###
#########################################################
idx <- which(test.data$userHasVotes == 1 & test.data$numUserSampleReviews <= 1)
data <- as.matrix(features.votes.nosamples(test.data[idx,]))
prediction[idx] <- predict(rf.votes.nosamples, data[,2:dim(data)[2]])

##############################################################
### users with no vote information but with sample reviews ###
##############################################################
idx <- which(test.data$userHasVotes == 0 & test.data$numUserSampleReviews > 1)
data <- as.matrix(features.novotes.samples(test.data[idx,]))
prediction[idx] <- predict(rf.novotes.samples, data[,2:dim(data)[2]])

######################################################
### users with vote information and review samples ###
######################################################
idx <- which(test.data$userHasVotes == 1 & test.data$numUserSampleReviews > 1)
data <- as.matrix(features.votes.samples(test.data[idx,]))
prediction[idx] <- predict(rf.votes.samples, data[,2:dim(data)[2]])

################################
### save predictions ro file ###
################################
prediction <- exp(prediction) - 1
prediction[prediction < 0] <- 0
write.table(data.frame(id=review.ids, votes=prediction), file=paste('predicted_votes_', SAVE_DATE, '.csv', sep=''),
            col.names=c("id", "votes"), row.names=F, quote=F, sep=',')
