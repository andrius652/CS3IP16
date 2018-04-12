import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import Qt, QtCore
from tweet_access import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import dropbox
import numpy as np
from matplotlib.pyplot import bar


# coding: utf-8

class MatplotlibWidget(QWidget):

    def __init__(self,parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)


        self.axis = self.figure.add_subplot(111)

        self.axis.set_facecolor('None')

        self.axis.spines['top'].set_color('#ffffff')
        self.axis.spines['bottom'].set_color('#ffffff')
        self.axis.spines['left'].set_color('#ffffff')
        self.axis.spines['right'].set_color('#ffffff')
        self.axis.set_ylabel("Amount")
        self.axis.set_xlabel("Sentiment")
        self.axis.tick_params(axis='x', colors='white')
        self.axis.tick_params(axis='y', colors='white')

        self.figure.set_size_inches(3,3)
        self.figure.patch.set_facecolor('None')

        self.layoutVertical = QVBoxLayout(self)  # QVBoxLayout
        self.layoutVertical.addWidget(self.canvas)


    def createGraph(self,sentiment):

        self.axis.clear()

        ind = np.arange(len(sentiment))

        width = 0.35

        self.axis.bar(ind - width / 2, sentiment, width, 0,  yerr=None, color='IndianRed', label='Positive')
        self.axis.set_xticks(ind)
        self.axis.set_xticklabels(('Positive', 'Neutral', 'Negative'))

        self.axis.get_children()[0].set_color('#25d622')
        self.axis.get_children()[1].set_color('#ff9933')
        self.axis.get_children()[2].set_color('#ed172d')


        self.figure.canvas.draw()








class Gui(QWidget):

    def __init__(self):
        super().__init__()



        self.twitter = TweetAccess().authorise()

        dropbox_token = 'e9Q_YzfArDAAAAAAAAAACqgOYoDLYreyezRekkkpCHMXRTsG7PEQymGp4mUScmh8'
        self.dbx = dropbox.Dropbox(dropbox_token)

        trendingWords = []
        trendingSentiment = ()

        self.dbx.files_download_to_file('trending.csv', '/' + 'TOP.csv')
        self.dbx.files_download_to_file('trending_sentiment.csv', '/' + 'trending_sentiment.csv')

        with open('trending.csv','r') as f:

            reader = csv.reader(f)

            for words in reader:

                trendingWords.append((words[0],words[1]))

        with open('trending_sentiment.csv', 'r') as f:

            reader = csv.reader(f)

            for words in reader:
                trendingSentiment = (words[0],words[1],words[2])
                print(trendingSentiment)

        QToolTip.setFont(QFont('Calibri',12))  # set tool tip font
        self.title = "TweetMan"  # set window title

        img = QImage('bg.png')
        palette = self.palette()
        palette.setBrush(10, QBrush(img))
        self.setPalette(palette)

        # palette = self.palette()  # take palette of window
        # palette.setColor(self.backgroundRole(), QColor(74,74,73))  # set palette colour
        #self.setPalette(palette)  # set window palette
        self.width = 1440
        self.height = 775
        self.posX = 2560 / 6
        self.posY = 1600 / 5

        self.currentTweets = []

        self.lib = MatplotlibWidget(self)
        self.lib.resize(380, 300)
        self.lib.move(0, 69)

        self.trending_graph = MatplotlibWidget(self)
        self.trending_graph.resize(380, 300)
        self.trending_graph.move(0, 420)
        self.trending_graph.createGraph((trendingSentiment[0], trendingSentiment[1], trendingSentiment[2]))

        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)


        #  blue: R - 67 :: G - 147 :: B - 214

        self.search_bar = QLineEdit(self)

        self.button = QPushButton('Find', self)  # assign button
        self.button.setToolTip("This is a <b>button</b> you sucker")  # set button tool tip
        self.button.resize(self.button.sizeHint())  # resize button
        self.button.setStyleSheet("""
                .QPushButton {
                    border: 4px solid rgb(67,147,214);
                    border-radius: 10px;
                    background-color: rgb(67,147,214);
                    color: white;
                    }
                """)

        self.progress = QProgressBar(self)
        self.progress.resize(240,30)

        self.positive = QPushButton('Positive', self)  # assign button
        self.positive.resize(80,30)  # resize button
        self.positive.setStyleSheet("""
                        .QPushButton {
                            border: 4px solid rgb(67,147,214);
                            border-radius: 10px;
                            background-color: rgb(67,147,214);
                            color: white;

                            }
                        """)

        self.negative = QPushButton('Negative', self)  # assign button
        self.negative.resize(80,30)  # resize button
        self.negative.setStyleSheet("""
                                .QPushButton {
                                    border: 4px solid rgb(67,147,214);
                                    border-radius: 10px;
                                    background-color: rgb(67,147,214);
                                    color: white;

                                    }
                                """)

        self.retrieve = QPushButton('Retrieve', self)  # assign button
        self.retrieve.resize(80, 30)  # resize button
        self.retrieve.setStyleSheet("""
                                        .QPushButton {
                                            border: 4px solid rgb(67,147,214);
                                            border-radius: 10px;
                                            background-color: rgb(67,147,214);
                                            color: white;

                                            }
                                        """)

        self.button.move(850, 4)  # move button to specific location
        self.positive.move(15,100)
        self.negative.move(15, 150)

        self.positive.setVisible(False)
        self.negative.setVisible(False)
        self.retrieve.move(1075,470)

        self.search_bar.resize(240, 30)  # search bar size, pos and style sheet
        self.search_bar.move(250, 20)
        self.search_bar.setText("")
        self.search_bar.setStyleSheet("""
        .QLineEdit {
            border: 4px solid rgb(67,147,214);
            border-radius: 10px;
            background-color: rgb(74, 74, 73);
            color: white;
            
            }
        """)


        self.tweetBox = QPlainTextEdit()
        self.tweetBox.resize(660, 80)  # tweet box size, pos and style sheet
        self.tweetBox.move(50, 50)
        self.tweetBox.setStyleSheet("""
                .QPlainTextEdit {
                    border: 4px solid rgb(67,147,214);
                    border-radius: 10px;
                    background-color: rgb(74, 74, 73);
                    color: rgb(255,255,255);
                    }
                """)

        self.search_bar.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)  # remove blue border
        self.tweetBox.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)

        self.button.pressed.connect(lambda: self.button_print(self.button))  # actions upon button being clicked
        self.button.released.connect(lambda: self.buttonReset(self.button))
        self.retrieve.pressed.connect(lambda: self.displaySelected())
        self.positive.pressed.connect(lambda: self.displayPositive())
        self.negative.pressed.connect(lambda: self.displayNegative())



        self.tweet_thread = TwitterThread(self.twitter)
        self.tweet_thread.updateText.connect(self.add_tweet)
        self.tweet_thread.deactivateButton.connect(self.enableButton)
        self.tweet_thread.set_top_words.connect(self.set_top_words)
        self.tweet_thread.set_tweets.connect(self.set_tweets)
        self.tweet_thread.setProgress.connect(self.getProgress)
        self.tweet_thread.start()



        #####################################

        self.scroll = QScrollArea(self)
        #scroll.setFrameShape(QFrame.NoFrame)

        self.scroll.resize(660,300)
        self.scroll.move(365,80)
        self.scroll.setWidgetResizable(True)  # CRITICAL

        self.boxlay = QVBoxLayout()

        self.inner = QFrame(self.scroll)
        self.inner.setLayout(self.boxlay)

        self.scroll.setWidget(self.inner)  # CRITICAL


        ##########################################

        self.listw = QListWidget(self)
        self.listw.resize(660,300)
        self.listw.move(365, 420)
        self.listw.setStyleSheet("""
                        .QListWidget {
                            border: 4px solid rgb(67,147,214);
                            border-radius: 10px;
                            background-color: rgb(74, 74, 73);
                            color: rgb(255,255,255);
                            }
                        """)

        self.location_list = QListWidget(self)
        self.location_list.resize(350, 300)
        self.location_list.move(1050, 80)
        self.location_list.setStyleSheet("""
                                .QListWidget {
                                    border: 4px solid rgb(67,147,214);
                                    border-radius: 10px;
                                    background-color: rgb(74, 74, 73);
                                    color: rgb(255,255,255);
                                    }
                                """)

        self.trending_list = QListWidget(self)
        self.trending_list.resize(350, 300)
        self.trending_list.move(1070, 460)
        self.trending_list.setStyleSheet("""
                                        .QListWidget {
                                            border: 4px solid rgb(67,147,214);
                                            border-radius: 10px;
                                            background-color: rgb(74, 74, 73);
                                            color: rgb(255,255,255);
                                            }
                                        """)

        for words in trendingWords:

            self.trending_list.addItem(words[0] + ", " + str(words[1]))

        tweets = QLabel(self)
        tweets.setText("Tweets")
        tweets.setFont(QFont("Calibri", 24))
        tweets.setStyleSheet("""
                            .QLabel {
                                color: rgb(255,255,255);
                                }
                            """)

        location = QLabel(self)
        location.setText("Tweet Locations")
        location.setFont(QFont("Calibri", 24))
        location.setStyleSheet("""
                                    .QLabel {
                                        color: rgb(255,255,255);
                                        }
                                    """)

        trending = QLabel(self)
        trending.setText("Trending Words")
        trending.setFont(QFont("Calibri", 24))
        trending.setStyleSheet("""
                                            .QLabel {
                                                color: rgb(255,255,255);
                                                }
                                            """)

        top_words = QLabel(self)
        top_words.setText("Top Words")
        top_words.setFont(QFont("Calibri", 24))
        top_words.setStyleSheet("""
                                    .QLabel {
                                        color: rgb(255,255,255);
                                        }
                                    """)

        tweets.move(345,50)
        location.move(1050,50)
        trending.move(1070, 430)
        top_words.move(345, 385)


        self.tweets = {}

        self.initUI()  # call initUI

    def displaySelected(self):

        for i in reversed(range(self.boxlay.count())):
            self.boxlay.itemAt(i).widget().setParent(None)

        sel = self.listw.selectedIndexes()[0]

        word = str(sel.data())

        word = word.split(",")

        selected_word = word[0]

        print(selected_word)

        for tweet in self.tweets:

            if selected_word in tweet[0].lower():
                self.add_tweet(tweet[0], tweet[1])


    def add_tweet(self, tweet, sentiment):

        tweetBox = QPlainTextEdit()
        tweetBox.setEnabled(False)

        tweetBox.setPlainText(tweet)

        #print(sentiment)


        if sentiment == 1:

            tweetBox.setStyleSheet("""
                                   .QPlainTextEdit {
                                       border: 2px solid rgb(37,214,34);
                                       border-radius: 10px;
                                       background-color: rgb(74, 74, 73);
                                       color: rgb(255,255,255);
                                       }
                                   """)

        if sentiment == 0:
            tweetBox.setStyleSheet("""
                                   .QPlainTextEdit {
                                       border: 2px solid rgb(237,23,45);
                                       border-radius: 10px;
                                       background-color: rgb(74, 74, 73);
                                       color: rgb(255,255,255);
                                       }
                                   """)

        if sentiment == 3:
            #print("NEUTRAL")
            tweetBox.setStyleSheet("""
                                   .QPlainTextEdit {
                                       border: 2px solid rgb(255,153,51);
                                       border-radius: 10px;
                                       background-color: rgb(74, 74, 73);
                                       color: rgb(255,255,255);
                                       }
                                   """)

        self.inner.layout().addWidget(tweetBox)

    def set_top_words(self, words, location):

        for i in words:

            self.listw.addItem(i[0] + ", " + str(i[1]))

        for i in location:

            self.location_list.addItem(i[0] + ", " + str(i[1]))

    def displayPositive(self):

        for i in reversed(range(self.boxlay.count())):
            self.boxlay.itemAt(i).widget().setParent(None)

        for tweet in self.pos_tweets:
            self.add_tweet(tweet, True)

    def displayNegative(self):

        for i in reversed(range(self.boxlay.count())):
            self.boxlay.itemAt(i).widget().setParent(None)

        for tweet in self.neg_tweets:
            self.add_tweet(tweet, False)

    def set_tweets(self, tweets):

        self.tweets = tweets

        pos = 0
        neut = 0
        neg = 0

        for i in range(0,300):
            self.add_tweet(self.tweets[i][0], self.tweets[i][1])

        for i in tweets:

            if i[1] == 0:
                neg = neg + 1

            if i[1] == 1:
                pos = pos + 1

            if i[1] == 3:
                neut = neut + 1

        self.lib.createGraph((pos,neut,neg))



    def enableButton(self):

        self.button.setEnabled(True)

    def initUI(self):  # create UI

        self.setWindowTitle(self.title)
        self.setGeometry(0, 0 , self.width, self.height)
        self.center()
        self.show()

    def center(self):  # center window to computer screen

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        self.move(qr.topLeft())

    def resizeEvent(self, event):  # on window resize

        self.widgetCenter(self.search_bar, 4)
        self.widgetCenter(self.progress, 30)
        print(self.height)


    def setButtonColor(self, button,  color):  # set button color

        pal = button.palette()
        pal.setColor(button.backgroundRole(), color)

        return pal


    def update(self):


        count = 0

        while count < 900:

            if len(self.currentTweets) > 0:
                count = count + 1
                #print(count)

    def button_print(self, button):  # button "print" actions


        for i in reversed(range(self.boxlay.count())):
            self.boxlay.itemAt(i).widget().setParent(None)


        self.tweetBox.clear()  # clear text box
        self.tweets.clear()
        self.listw.clear()
        self.tweet_thread.setSearch(self.search_bar.text())
        self.tweet_thread.setPause(False)


        #thread = Thread(target=self.update)
        #thread.start()

        button.setStyleSheet("""
                        .QPushButton {
                            border: 4px solid rgb(67,147,214);
                            border-radius: 10px;
                            background-color: rgb(74,74,73);
                            color: white;
                            }
                        """)

    def buttonReset(self, button):  # after button has been clicked

       # print("Current Tweets: ", self.currentTweets)

        button.setStyleSheet("""
                                                .QPushButton {
                                                       border: 4px solid rgb(67,147,214);
                                                       border-radius: 10px;
                                                       background-color: rgb(67,147,214);
                                                       color: white;
                                                       }
                                                   """)

        self.button.setEnabled(False)




    def widgetCenter(self, widget, y):  # center widget to window

        gm = self.frameGeometry()

        widget.move((gm.width()/2) - (widget.width()/2), y)


    def getProgress(self, percent):

        #print("dehello")

        self.progress.setValue(percent)




