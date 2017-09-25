import nltk
import csv
import re
import time,datetime
from nltk.stem.porter import PorterStemmer


http_regex = "https?://[\w\/_\.-]*"

# regrex contains mentions and hashtags
twitter_regex_withAtHashtags = "[@#a-zA-Z_]{3,}|[A-Z]{2,}"

# regrex dones not contains mentions and hashtags
twitter_regex = "[a-zA-Z_]{3,}|[A-Z]{2,}"

def tokenise_tweet(tweet, stopwordlist, regex = twitter_regex_withAtHashtags, isStem = False):
    tokens = nltk.regexp_tokenize(re.sub(http_regex, '', tweet.lower()), regex)
    ps = PorterStemmer()
    if isStem:
        return [str(ps.stem(w)) for w in tokens if w not in stopwordlist]
    else:
        return [w for w in tokens if w not in stopwordlist]

def remove_url(text):
    http_regex = "https?://[\w\/_\.-]*"
    return re.sub(http_regex, '', text)

def return_tweet_timestamp(time_string):
    return long(time.mktime(datetime.datetime.strptime(time_string, '%a %b %d %H:%M:%S +0000 %Y').timetuple()))

class csvLib:
    def __init__(self, delimiter=','):
        self.delimiter = delimiter
        self.CSVfileList = {}
        self.CSVwriterList = {}
        self.fileList = {}

    def writeLine(self, filename, line):
        if filename in self.fileList:
            self.fileList[filename].write(line + '\n')
        else:
            self.fileList[filename] = open(filename, 'wb')
            self.fileList[filename].write(line + '\n')

    def writeCSVLine(self, filename, lineList):
        if filename in self.CSVwriterList:
            self.CSVwriterList[filename].writerow(lineList)
        else:
            self.CSVfileList[filename] = open(filename, 'wb')
            self.CSVwriterList[filename] = csv.writer(self.CSVfileList[filename], delimiter=self.delimiter)
            self.CSVwriterList[filename].writerow(lineList)

    def closeCSVWriters(self):
        for file in self.CSVfileList:
            self.CSVfileList[file].close()

    def closeWriters(self):
        for file in self.fileList:
            self.fileList[file].close()

    def readCSV(self, filename):
        data=[]
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter,)
            for row in reader:
                data.append(list(row))
        return data

    def readFileLineByLine(self, filename):
        data=[]
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter,)
            for row in reader:
                data.extend(row)
        return data



