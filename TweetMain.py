import tweepy
import csv
import nltk
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtCore
from nltk.corpus import stopwords
import string
import threading
from queue import Queue
from time import sleep
from multiprocessing import Process
import multiprocessing as mp
from unicodedata import normalize
import sys
import time

class Miner:

    def __init__(self):
        self.amount_negative = 0
        self.amount_positive = 0

        self.stop_words = set(stopwords.words("english"))

        self.probability = {}
        self.local_probability = {}

        self.openTrainingData()


    def openTrainingData(self):

        total_vocab = set()
        amount_positive = 0
        amount_neutral = 0
        amount_negative = 0
        allwords = []

        with open("allwords.csv", 'r') as file:

            reader = csv.reader(file)

            for i in reader:

                if i[1] is not '0':
                    amount_positive = amount_positive + int(i[1])

                if i[2] is not '0':
                    amount_neutral = amount_neutral + int(i[2])

                if i[3] is not '0':
                    amount_negative = amount_negative + int(i[3])

                allwords.append(i)
                total_vocab.add(i[0])

        pos_denominator = amount_positive + len(total_vocab)
        neg_denominator = amount_negative + len(total_vocab)
        neut_denominator = amount_neutral + len(total_vocab)

        for i in allwords:
            self.probability[i[0]] = (((float(i[1]) + 1) / pos_denominator, (float(i[2]) + 1) / neut_denominator,
                                    (float(i[3]) + 1) / neg_denominator))

            print(self.probability[i[0]])

    # amount + 1 / amount_pos/amount_neg + total_vocab

    def returnNouns(self, text):


        tokenized = nltk.pos_tag(text)
        nouns = []

        for i in tokenized:

            if i[1] == "NN" or i[1] == 'JJ':
                #print(i)
                nouns.append(i[0])

        return nouns

    def clear(self):
        self.local_probability.clear()

    def appendToLocal(self,tweet):

        text1 = ""

        for i in tweet:

            if i not in string.punctuation and 'http' not in i:
                text1 = text1 + i

        text1 = nltk.word_tokenize(text1.lower())

        for i in text1:

            if i in self.local_probability:
                pass

            elif i in self.probability:

                self.local_probability[i] = self.probability[i]

    def preprocess(self, text): # returns sentiment and nouns/adjectives associated with the text

        final_text = []
        processed_tweets = set()

        #print(text)

        text1 = ""

        for i in text:

            if i not in string.punctuation:
                text1 = text1 + i

        #print(text1)


        new_text = nltk.word_tokenize(text1.lower())


        negative_prob = 0
        neut_prob = 0
        positive_prob = 0

        for i in new_text:

            if i not in self.stop_words and "http" not in i:
                final_text.append(i)

        #print(final_text)

        nouns = self.returnNouns(final_text)

        for i in final_text:



            if i in self.probability:

                positive_prob = positive_prob + float(self.probability[i][0])
                neut_prob = neut_prob + float(self.probability[i][1])
                negative_prob = negative_prob + float(self.probability[i][2])

        result = -1

        if negative_prob >= positive_prob and negative_prob >= neut_prob:
            result = 0

        if positive_prob >= negative_prob and positive_prob >= neut_prob:
            result = 1

        if neut_prob >= negative_prob and neut_prob >= positive_prob:
            result = 3


        return result, nouns



class TweetAccess:

    def __init__(self):
        self.twitter = self.authorise()
        self.lastSearched = ""


    def authorise(self):
        __consumerKey = 
        __consumerSecret = 
        __accessToken = 
        __accessSecret = 

        auth = tweepy.AppAuthHandler(__consumerKey, __consumerSecret)
        #auth.set_access_token(__accessToken, __accessSecret)



        return tweepy.API(auth)


class TwitterThread(QThread):

    updateText = pyqtSignal(str, int)
    deactivateButton = pyqtSignal()
    setProgress = pyqtSignal(float)
    set_top_words = pyqtSignal(list,list)
    set_tweets = pyqtSignal(list)

    def __init__(self, twitter):
        QtCore.QThread.__init__(self)
        self.twitter = twitter
        self.search = ""
        self.pause = True
        self.Miner = Miner()
        self.topWords = []
        self.tweets = []

        self.countries = []
        self.states = []
        self.tweets = []


        self.openLocations()



    def setSearch(self, search):

        self.search = search

    def returnQueue(self):

        return self.mainQueue

    def setPause(self, flag):
        self.pause = flag

    def openLocations(self):

        countries = open('countries.txt', 'r')

        for i in countries:
            i = str(i)
            new = i.replace('\n', '')
            new = new.strip()
            self.countries.append(new)

        for i in self.countries:
            print(i)

        with open('states.csv', 'r', errors='replace') as f:

            reader = csv.reader(f)

            for i in reader:

                self.states.append(i)

        for j in self.states:
            print(j)


    def run(self):

        count = 0

        while True:

            self.sleep(1)

            while self.pause is False:

                locations = set()
                tweets = []


                searchName = self.search + " -filter:retweets"

                for tweet in tweepy.Cursor(self.twitter.search,
                                           q=searchName,
                                           count=100,
                                           tweet_mode="extended",
                                           result_type="recent",
                                           include_entities=True,
                                           lang="en").items(1000):


                    val = ""

                    val = val + tweet.full_text + "\n"

                    if (len(tweet.user.location) > 1):
                        locations.add(tweet.user.location)

                    tweets.append(val)

                    #self.Miner.appendToLocal(val)

                    count = count + 1

                    self.setProgress.emit((count/1000) * 100)

                #print("finished")

                ##############################################################
                ##############################################################

                start_time = time.time()

                count = 0

                for tweet in tweets:

                    count = count + 1

                    sentiment, nouns = self.Miner.preprocess(tweet)

                    for word in nouns:
                        self.topWords.append(word)

                    if sentiment == 1:
                        self.tweets.append((tweet, 1))

                    if sentiment == 0:
                        self.tweets.append((tweet, 0))

                    if sentiment == 3:
                        self.tweets.append((tweet,3))

                    #self.updateText.emit(tweet,sentiment)

                    print(count)

                print("Program took: ", time.time() - start_time)

                ###################################################################
                ###################################################################
                #self.Miner.printStats()
                freq = nltk.FreqDist(self.topWords)
                #print(freq.most_common(30))
                self.setPause(True)
                print("Finished acquiring tweets")
                cnt_list = []
                final_cnt = []

                for i in locations:

                    for j in self.countries:

                        if j in i:
                            if j == "USA" or j == 'America':
                                cnt_list.append("United States")
                                #print("United States")

                            if j == "England" or j == "Wales" or j == "Scotland":
                                #print("United Kingdom")
                                cnt_list.append("United Kingdom")

                            else:

                                if j == "USA" or j == "America":
                                    cnt_list.append("United States")
                                else:
                                   # print(j)
                                    cnt_list.append(j)

                    for j in self.states:

                        if j[1] in i or j[0] in i:
                            cnt_list.append("United States")

                for i in self.countries:

                    count = 0

                    for j in cnt_list:

                        if i == j:
                            count = count + 1

                    if count > 0:
                        final_cnt.append((i, count))

                final_cnt = sorted(final_cnt, key=lambda x: x[1], reverse=True)

                self.deactivateButton.emit()
                self.set_top_words.emit(freq.most_common(len(freq)), final_cnt)
                self.set_tweets.emit(self.tweets)
                self.topWords.clear()
                self.tweets.clear()
                self.Miner.clear()




        print("Terminating Thread")


