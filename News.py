import re
import nltk
import requests
from utils import *
import dateutil.parser
import credentials as creds
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from nltk.corpus import stopwords
from datetime import date, timedelta
from newsdataapi import NewsDataApiClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class gatherNews:
    def __init__(self) -> None:
        # genralNews = self.RssFeedNews() + self.InshortNews()
        # categorizedNews = []
        # for news in genralNews:
        #     companyName, companySymbol = GetCompanyDetails(news)
        #     if(companyName):
        #         categorizedNews.append([companyName, news])
        # self.Morning = categorizedNews
        pass

    def GetNewsApiNews(companyName: str) -> list:
        api = NewsApiClient(api_key=creds.NEWS_API_KEY)
        companyName = '"' + companyName + '"'
        articles = api.get_everything(q=companyName, qintitle=companyName, language='en', page_size=100)['articles']
        newsDescriptions = [news['description'] for news in articles]
        return newsDescriptions

    def GetNewsdataNews(companyName: str) -> list:
        api = NewsDataApiClient(apikey=creds.NEWS_DATA_KEY)
        articles = api.news_api(country='in',q=companyName, language='en')['results']
        newsDescriptions = [news['description'] for news in articles]
        return newsDescriptions
    
    def RssFeedNews() -> list:
        sources = [
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "https://economictimes.indiatimes.com/markets/expert-view/rssfeeds/50649960.cms",
        "https://www.moneycontrol.com/rss/marketoutlook.xml",
        "https://www.moneycontrol.com/rss/marketedge.xml"
        ]
        today = date.today()
        newsDescriptions = []
        articleComponents = ['title','description']
        for source in sources:
            response = requests.get(source)
            content = BeautifulSoup(response.content, features='xml')
            articles = content.findAll('item')
            for article in articles:
                News = ""
                articleDate = dateutil.parser.parse(article.find('pubDate').text).date()
                if(today-articleDate < timedelta(days = 3)):
                    for component in articleComponents:
                        News += article.find(component).text
                    newsDescriptions.append(News)
        return newsDescriptions

    def InshortNews() -> list:
        sources = [
        "https://www.inshorts.com/en/read/startup",
        "https://www.inshorts.com/en/read/business",
        "https://www.inshorts.com/en/read/technology"
        ]
        newsDescriptions = []
        for source in sources:
            response = requests.get(source)
            content = BeautifulSoup(response.content, features='html.parser')
            articles = content.findAll('div')
            for article in articles:
                if(article.get('itemprop') == 'articleBody'):
                    newsDescriptions.append(article.text)
        return newsDescriptions

class NewsClassifer:
    def __init__(self) -> None:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('vader_lexicon')
        nltk.download('averaged_perceptron_tagger')
        self.SIA = SentimentIntensityAnalyzer()
        financial_word_classification = {"bullish": 1, "bearish": -1, "volatile": -0.3, "risen": 0.5, "fell": -0.5, "growth": 0.5, "rally": 0.5, "buy": 0.7, "sell":-0.7} #add other words
        self.SIA.lexicon.update(financial_word_classification)
        self.EN_STOP_WORDS = stopwords.words('english')
    
    def RemoveNonAscii(self, sentence: str ) -> str: 
        return "".join(i for i in sentence if ord(i)<128)
    
    def CleanText(self, sentence: str ) -> str:
        sentence = sentence.lower()
        sentence = self.RemoveNonAscii(sentence)
        sentence = re.sub(r"what's", "what is ", sentence)
        sentence = sentence.replace('(ap)', '')
        sentence = re.sub(r"\'s", " is ", sentence)
        sentence = re.sub(r"\'ve", " have ", sentence)
        sentence = re.sub(r"can't", "cannot ", sentence)
        sentence = re.sub(r"n't", " not ", sentence)
        sentence = re.sub(r"i'm", "i am ", sentence)
        sentence = re.sub(r"\'re", " are ", sentence)
        sentence = re.sub(r"\'d", " would ", sentence)
        sentence = re.sub(r"\'ll", " will ", sentence)
        sentence = re.sub(r'\W+', ' ', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
        sentence = re.sub(r"\\", "", sentence)
        sentence = re.sub(r"\'", "", sentence)    
        sentence = re.sub(r"\"", "", sentence)
        sentence = re.sub('[^a-zA-Z ?!]+', '', sentence)
        return sentence

    def RemoveStopwords(self, sentence: str, stopwords: list = [] ) -> str:
        words = sentence.split() 
        stopwords = self.EN_STOP_WORDS + stopwords
        filtered_sentence = [w for w in words if not w in stopwords]
        return " ".join(filtered_sentence)

    def vanderPrediction(self, sentence: str) -> int:
        try:
            sentence = self.CleanText(sentence)
            sentence = self.RemoveStopwords(sentence)
            polarity = self.SIA.polarity_scores(sentence)
            if(polarity['compound'] >= 0.1):
                return 1
            elif(polarity['compound'] <= -0.1):
                return -1
        except:
            return 0
        return 0