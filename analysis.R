library(quanteda)
# library(pgirmess)
library(fifer)
library(syuzhet)

# Load comments and word lists.
# [comments_x.csv + comments_y.csv + ... > comments.csv]
# [videos_x.csv + videos_y.csv + ... > videos.csv]
comments <- merge(
  read.csv("./comments_UCtinbF-Q-fVthA0qrFQTgXQ.csv", stringsAsFactors=FALSE),
  read.csv("./videos_CaseyNeistat.csv", stringsAsFactors=FALSE)
)
comments$channelTitle <- as.factor(comments$channelTitle)
comments$videoTitle <- as.factor(comments$videoTitle)
# Swear Words & Curse Words
# Source: http://www.noswearing.com/dictionary
badWords <- readLines("badwords.txt")

# Word list of channel specific names (e.g., conan, pewdiepie)
names <- readLines("names.txt")

# Tokenize comments
toks <- tokenize(tolower(comments$text),
                 removeNumbers = TRUE,
                 removePunct = TRUE,
                 removeSeparators = TRUE,
                 removeSymbols = TRUE,
                 removeHyphens = TRUE,
                 removeURL = TRUE)

# Count profane words
comments$word_cnt <- ntoken(toks)
toksProfane <- selectFeatures(toks, badWords, selection = "keep")

# Define dummy variables for use of profanity and sentiment
comments$is_profane <- ifelse(ntoken(toksProfane)>0, 1, 0)
comments$sentimentScore <- get_sentiment(comments$text, method="bing")
comments$polarity <- ifelse(comments$sentimentScore>0, "positive",
                             ifelse(comments$sentimentScore<0, "negative", "neutral"))

# Plot comparison cloud.
commentsDfm <- dfm(toks, groups = comments$channelTitle,
                   remove = c(stopwords("english"), names))
#set.seed(12345)
#textplot_wordcloud(dfm_select(commentsDfm, min_nchar=1),
#                   comparison=TRUE,
#                   random.order=FALSE,
#                   colors = c("#00c853"),
#                   family="Lato Medium",
#                   max.words=250,
#                   title.size=1.5)

# Generate contingency tables.
cTable.profane <- table(comments[,c("videoTitle", "is_profane")])
cTable.polarity <- table(comments[,c("videoTitle", "polarity")])
prop.table(cTable.profane, 1)
prop.table(cTable.polarity, 1)

# Use the Kruskal–Wallis test to check whether the average number of 
# words per comment differes signigicantly between the four categories
kruskal.test(word_cnt~videoTitle, data=comments)
kruskalmc(word_cnt~videoTitle, data=comments)

# Use the chi-square test of Independence to check whether the 
# profanity/polarity dummies differ signigicantly between the four categories.
chisq.test(cTable.profane)
chisq.test(cTable.polarity)
chisq.post.hoc(cTable.profane, test=chisq.test)
chisq.post.hoc(cTable.polarity, test=chisq.test)

