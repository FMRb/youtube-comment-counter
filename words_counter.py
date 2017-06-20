import csv
from textblob import TextBlob
import operator

total_text = ''
with open('comments_FleurDeVlog.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=",", quotechar = '|')
    for row in spamreader:
        text = row[3].lower()
        if not text.endswith('.'):
            text = text + '.'
        if not text.endswith(' '):
            text = text + ' '
        
        total_text = total_text + text


comments = TextBlob(total_text)
setCommentWords = set(comments.words)

freq = {}
for word in setCommentWords:
    freq[word] = comments.word_counts[word]
sortedwords = sorted(freq.items(), key=operator.itemgetter(1), reverse=True);

with open("words_count_fleurdevlog.csv", "wb+") as wordFile:
    wordWriter = csv.writer(wordFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    wordWriter.writerows([[
        "word",
        "number"
    ]])
    for word in sortedwords:
        wordWriter.writerows([[
            word[0],
            word[1]
        ]])

# cap_words = [word.upper() for word in words]

# word_counts = Counter(cap_words)