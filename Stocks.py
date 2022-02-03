import requests
import pandas as pd
import yfinance as yf
from utils import MongoDB
from bs4 import BeautifulSoup 
from pandas.core.frame import DataFrame

class StocksInfo:
    def __init__(self) -> None:
        companyStopWords =['limited', 'ltd', 'services']
        db = MongoDB()
        nseData = db.RetriveData('nseList')
        cleanName = []
        for name in nseData['Name']:
            name = name.lower()
            for word in companyStopWords:
                if word in name:
                    name = name.split(word)[0][:-1]
            cleanName.append(name)
        nseData['CleanName'] = pd.DataFrame(cleanName, columns = ['CleanName'] )
        self.nseData = nseData

    def GetActiveStocks(self) -> list:
        mainLink = 'https://www.moneycontrol.com'
        source = "https://www.moneycontrol.com/stocks/marketinfo/invest/nse/index.html"
        activeStocks = []
        response = requests.get(source)
        content = BeautifulSoup(response.content, features='html.parser')
        allAchors = content.findAll('a')
        for achor in allAchors:
            try:
                if('bl_12' in achor.get('class')):
                    response = requests.get(mainLink+achor.get('href'))
                    content = BeautifulSoup(response.content, features='html.parser')
                    stockName = content.find('div',  {"id": "stockName"})
                    activeStocks.append(stockName.find('h1').text)
            except:
                pass
        return activeStocks
    
    def GetHistoricalData(self, symbol: str, time_period: str, time_interval: str) -> DataFrame:
        symbol += ".NS"
        historicalData =yf.Ticker(symbol).history(period = time_period, interval = time_interval)
        historicalData = historicalData.drop(['Dividends', 'Stock Splits'],axis=1)
        return historicalData

    def FindCompany(self, sentence: str) -> str:
        sentence = sentence.lower()
        # companyName = ''
        symbol = ''
        subNameLen = 0
        # for Cleanname in self.nseData['CleanName']:
        for i  in range(len(self.nseData)):
            Cleanname = self.nseData['CleanName'][i]
            subName = ''
            for subNames in Cleanname.split():
                subName += subNames + ' '
                if(len(subNames) > 1):
                    if(subName[:-1] in sentence and len(subName) > subNameLen):
                        # companyName = subName
                        subNameLen = len(subName)
                        symbol = self.nseData['Symbol'][i]
        if(not symbol):
            return ''
        return symbol
    
    def GetStockSymbol(self, stockName: str) -> str:
        stockName = stockName.upper()
        for symbol in self.nseData['Symbol']:
            if(stockName == symbol):
                return symbol
        return self.FindCompany(stockName)

class TradeStocks:
    def __init__(self) -> None:
        pass

    def BuyStock(self, symbol: str, quantity: int, buyPrice: float, stopLossPrice: float) -> bool:
        print("bought ", symbol)
        return True
    
    def SellStock(self, symbol: str, quantity: int, sellPrice: float) -> bool:
        print("Sold", symbol)
        return True

