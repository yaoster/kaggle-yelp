INPUT_FILE <- '../data/business_categories.csv'
OUTPUT_FILE <- '../data/business_categories_clustered.csv'
data <- read.csv(INPUT_FILE, sep=',', header=T, as.is=T)

cluster.errors <- function(clusters)
{
    withinss <- rep(0, length(clusters))
    counter <- 1
    for (i in clusters) {
        print(i)
        cluster <- kmeans(data[,2:dim(data)[2]], i, iter.max=100, nstart=5)
        withinss[counter] <- cluster$tot.withinss
        print(100 - 100*cluster$tot.withinss/cluster$totss)
        counter <- counter + 1
    }
    return(data.frame(withinss=withinss, pctvar=(100-100*withinss/cluster$totss)))
}

print.cluster.info <- function(cluster)
{
    for (i in 1:length(cluster$size)) {
        s <- paste('size', cluster$size[i], sep=':')
        s <- paste(s, '', sep=',')
        sj <- ''
        centers <- sort(cluster$centers[i,], decreasing=T)[1:5]
        for (j in 1:5) {
            sj <- paste(sj, names(centers)[j], sep=':')
            sj <- paste(sj, (centers)[j], sep=', ')
        }
        s <- paste(s, sj, sep='')
        print(s)
    }
}

write.cluster.info <- function(cluster)
{
    data.out <- data.frame(id=data$id, category=cluster$cluster)
    write.table(data.out, file=OUTPUT_FILE, col.names=T, row.names=F, quote=F, sep=',')
}

#result <- clusterErrors(25:75)
