import os 
import cv2
import talib
import numpy as np
from time import sleep
from selenium import webdriver
import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
ZIA_INDICATOR_URL = 'https://in.tradingview.com/chart/X3BxHYtc/?symbol='
CWD = os.getcwd()

class Indicators:
    def __init__(self) -> None:
        chromeOptions = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": CWD, 
            "directory_upgrade": True
            }        
        chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument("--headless")
        self.webDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)

    def Zia(self, symbol: str ) -> int:
        self.webDriver.get(ZIA_INDICATOR_URL + symbol)
        sleep(5)
        self.webDriver.find_element(By.ID, 'header-toolbar-screenshot').click()
        sleep(1)
        self.webDriver.find_elements(By.CLASS_NAME, "withIcon-NklSvNSQ")[0].click()
        sleep(1)
        imagePath = CWD + "/" + [name for name in os.listdir(CWD) if(symbol in name) ][-1]
        image=cv2.imread(imagePath)
        os.remove(imagePath)
        img_hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_red = np.array([170,50,50])
        upper_red = np.array([180,255,255])
        red_mask = cv2.inRange(img_hsv, lower_red, upper_red)
        lower_green = np.array([40, 40,40])
        upper_green = np.array([70, 255,255])
        green_mask = cv2.inRange(img_hsv, lower_green, upper_green)
        try:
            redMaskCount = np.amax(np.where(red_mask == 255))
        except:
            return 1
        try:
            greenMaskCount = np.amax(np.where(green_mask == 255))
        except:
            return -1
        if(redMaskCount>greenMaskCount):
            return -1
        return 1

    def MACD(self, prices: DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> int:
        macd, macdsignal, macdhist = talib.MACD(prices, fastperiod, slowperiod, signalperiod)
        if(macd[-1] > macdsignal[-1]):
            return 1
        elif(macd[-1] < macdsignal[-1]):
            return -1
        return 0        

    def RSI(self, prices: DataFrame, timeperiod: int = 14) -> int:
        rsi = talib.RSI(prices, timeperiod)
        if (rsi[-2] > 30 and rsi[-1] < 30):
            return 1
        elif (rsi[-2]< 70 and rsi[-1] > 70):
            return -1
        return 0

    def BBands(self, prices: DataFrame, timeperiod: int = 10) -> int:
        upperband, middleband, lowerband = talib.BBANDS(prices, timeperiod)
        if (prices[-1] < lowerband[-1] and prices[-1]>prices[-2]):
                return 1
        elif (prices[-1] > upperband[-1] and prices[-1]<prices[-2]):
            return -1
        return 0

    def DEMA(self, prices: DataFrame, timeperiod1: int = 14, timeperiod2: int = 21) -> int:
        ema1 = talib.EMA(prices, timeperiod1)
        ema2 = talib.EMA(prices, timeperiod2)
        if(ema1[-1] > ema2[-1]):
            return 1
        elif(ema1[-1] < ema2[-1]):
            return -1
        return 0

class Patterns:
    def __init__(self) -> None:
        pass

    def Marubozu(self, data: DataFrame) -> int:
        todaysData = data.iloc[-1]
        data = data.iloc[:-1]
        marubozuPattern = talib.CDLMARUBOZU(data['Open'], data['High'], data['Low'], data['Close'])
        if(marubozuPattern[-1] == 100):
            if(todaysData['Open'] > data.iloc[-1]['Close']):
                return 1
            return 0
        elif(marubozuPattern[-1] == -100):
            if(todaysData['Open'] < data.iloc[-1]['Close']):
                return -1
            return 0
        return 0

    def Engulfing(self, data: DataFrame) -> int:
        engulfingPattern = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])
        if(engulfingPattern[-1]== 100):
            return 1
        elif(engulfingPattern[-1] == -100):
            return -1
        return 0
    
    def Hammer(self, data: DataFrame) -> int:
        todaysData = data.iloc[-1]
        data = data.iloc[:-1]
        hammerPattern = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
        if(hammerPattern[-1]== 100):
            if(todaysData['Open'] > data.iloc[-1]['Close']):
                return 1
            return 0
        return 0
    
    def ShootingStar(self, data: DataFrame) -> int:
        todaysData = data.iloc[-1]
        data = data.iloc[:-1]
        shootingStarpattern = talib.CDLSHOOTINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
        if(shootingStarpattern[-1] == -100):
            if(todaysData['Open'] > data.iloc[-1]['Close']):
                return -1
            return 0
        return 0

    def Harami(self, data: DataFrame) -> int:
        haramiCPattern = talib.CDLHARAMICROSS(data['Open'], data['High'], data['Low'], data['Close'])
        if(haramiCPattern[-1]== 100):
            return 1
        elif(haramiCPattern[-1] == -100):
            return -1
        return 0

    def MorningStar(self, data: DataFrame) -> int:
        morningStarPattern = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'], penetration=0)
        if(morningStarPattern[-1] == 100):
            return 1
        return 0
        
    def EveningStar(self, data: DataFrame) -> int:
        eveningStarPattern = talib.CDLEVENINGSTAR(data['Open'], data['High'], data['Low'], data['Close'], penetration=0)
        if(eveningStarPattern[-1] == -100):
            return 1
        return 0

    def DowTheory(self, prices: DataFrame, timeFrame: int = 7) -> int:
        priceToday = prices.iloc[-1]
        prices = prices.iloc[:-1].to_numpy()
        peaks = np.where((prices[1:-1] > prices[0:-2]) * (prices[1:-1] > prices[2:]))[0] + 1
        dips = np.where((prices[1:-1] < prices[0:-2]) * (prices[1:-1] < prices[2:]))[0] + 1
        upperLimit = 0
        lowerLimit = 0
        bearishDow = []
        for i in range(len(peaks)-1,0,-1):
            localDow = []
            while(abs(prices[peaks[i]] - prices[peaks[i-1]]) < priceToday/100):
                if(peaks[i]  not in localDow ):
                    localDow.append(peaks[i])
                if(peaks[i-1]  not in localDow):
                    localDow.append(peaks[i-1])
                i -= 1
            if(len(localDow)):
                for i in range(len(localDow)-1):
                    for j in range(i+1,len(localDow)):
                        if(abs(localDow[i]-localDow[j])>=timeFrame):
                            bearishDow.append([localDow[i],localDow[j]])
                            upperLimit = max(upperLimit,prices[localDow[i]],prices[localDow[j]])
            i += 1
        bullishDow = []
        for i in range(len(dips)-1,0,-1):
            localDow = []
            while(abs(prices[dips[i]] - prices[dips[i-1]]) < priceToday/100):
                if(dips[i]  not in localDow):
                    localDow.append(dips[i])
                if(peaks[i-1]  not in localDow):
                    localDow.append(dips[i-1])
                i -= 1
            if(len(localDow)):
                for i in range(len(localDow)-1):
                    for j in range(i+1,len(localDow)):
                        if(abs(localDow[i]-localDow[j])>=timeFrame):
                            bullishDow.append([localDow[i],localDow[j]])
                            lowerLimit = max(lowerLimit,prices[localDow[i]],prices[localDow[j]])
            i += 1
        # print("Dow tops:", bearishDow)
        # print("Dow Bottoms:", bullishDow)
        # print("upperLimit:",upperLimit,"lowerLimit:", lowerLimit, "priceToday:", priceToday)

        if(upperLimit > priceToday and priceToday < lowerLimit):
            return 1 if abs(priceToday - lowerLimit) else -1
        else:
            return 0 

    def SandR(self, prices: DataFrame, days: int = 60) -> int:
        priceToday = prices.iloc[-1]
        diffCheck = priceToday/50
        if(len(prices) > days):
            prices = prices.iloc[days:-1].to_numpy()
        else:
            prices = prices.iloc[:-1].to_numpy()
        peaks = np.where((prices[1:-1] > prices[0:-2]) * (prices[1:-1] > prices[2:]))[0] + 1
        dips = np.where((prices[1:-1] < prices[0:-2]) * (prices[1:-1] < prices[2:]))[0] + 1
        print("priceToday:", priceToday)
        
        resistance = 0
        for i in range(len(peaks)-1,1,-1):
            for j in range(i-1,0,-1):            
                if(abs(prices[peaks[i]] - prices[peaks[j]]) < diffCheck):
                    resistance = max(resistance,prices[peaks[i]] if prices[peaks[i]]>prices[peaks[i-1]] else  prices[peaks[i-1]] )

        if(resistance == 0):
            resistance = max(prices)
            resistance2 = max(prices[prices<resistance])
        elif(len(prices[prices>resistance])):
            resistance2 = max(prices[prices>resistance])
        else:
            resistance2 = resistance

        print("resistance 1:", resistance, 'resistance 2:', resistance2)
        
        support = priceToday
        for i in range(len(dips)-1,1,-1):
            for j in range(i-1,0,-1):  
                if(abs(prices[dips[i]] - prices[dips[j]]) < diffCheck):
                    support = min(support,prices[dips[i]] if prices[dips[i]]<prices[dips[i-1]] else  prices[dips[i-1]] )
        
        # if(support == priceToday):
        #     support = prices[dips[-1]]
        #     support2 = prices[dips[-2]]

        if(len(prices[prices<support])):
            support2 = max(prices[prices<support])
        else:
            support2 = support
        print("support 1:",support, 'Support 2:',support2)

        if(resistance > priceToday and priceToday > support):
            if(abs(resistance - priceToday) < diffCheck):
                return -1
            elif(abs(support - priceToday) < diffCheck):
                return 1
            return 0

        elif(resistance < priceToday):
            if(abs(resistance2 - priceToday) < diffCheck):
                return -1
            elif(abs(resistance - priceToday) < diffCheck):
                return 1
            return 0

        elif(support > priceToday):
            if(abs(support2 - priceToday) < diffCheck):
                return 1
            elif(abs(support - priceToday) < diffCheck):
                return -1
            return 0
        return 0

    def SandR1(self, prices: DataFrame, days: int = 60) -> int:
        priceToday = prices.iloc[-1]
        diffCheck = priceToday/50
        resistance = 0
        superResistance = 0
        support = priceToday
        superSupport = priceToday
        print("priceToday:", priceToday)
        if(len(prices) > days):
            prices1 = prices.iloc[-days:-1].to_numpy()
            prices2 = prices.iloc[-days//2:-1].to_numpy()
        else:
            prices1 = prices.iloc[:-1].to_numpy()
            prices2 = prices.iloc[len(prices)//2:-1].to_numpy()
        prices = prices.to_numpy()

        peaks1 = np.where((prices1[1:-1] > prices1[0:-2]) * (prices1[1:-1] > prices1[2:]))[0] + 1
        peaks2 = np.where((prices2[1:-1] > prices2[0:-2]) * (prices2[1:-1] > prices2[2:]))[0] + 1
        dips1 = np.where((prices1[1:-1] < prices1[0:-2]) * (prices1[1:-1] < prices1[2:]))[0] + 1
        dips2 = np.where((prices2[1:-1] < prices2[0:-2]) * (prices2[1:-1] < prices2[2:]))[0] + 1
        
        for i in range(len(peaks2)-1,1,-1):
            for j in range(i-1,0,-1):            
                if(abs(prices2[peaks2[i]] - prices2[peaks2[j]]) < diffCheck):
                    resistance = max(resistance,prices2[peaks2[i]] if prices2[peaks2[i]]>prices2[peaks2[i-1]] else  prices2[peaks2[i-1]] )
        
        for i in range(len(peaks1)-1,1,-1):
            for j in range(i-1,0,-1):            
                if(abs(prices1[peaks1[i]] - prices1[peaks1[j]]) < diffCheck):
                    superResistance = max(superResistance,prices1[peaks1[i]] if prices1[peaks1[i]]>prices1[peaks1[i-1]] else  prices1[peaks1[i-1]] )
        if(resistance >= superResistance):
            superResistance = max(prices1)

        print("resistance:",resistance,"superResistance:",superResistance)

        for i in range(len(dips2)-1,1,-1):
            for j in range(i-1,0,-1):            
                if(abs(prices2[dips2[i]] - prices2[dips2[j]]) < diffCheck):
                    support = min(support,prices2[dips2[i]] if prices2[dips2[i]]<prices2[dips2[i-1]] else  prices2[dips2[i-1]] )
        
        for i in range(len(dips1)-1,1,-1):
            for j in range(i-1,0,-1):            
                if(abs(prices1[dips1[i]] - prices1[dips1[j]]) < diffCheck):
                    superSupport = min(superSupport,prices1[dips1[i]] if prices1[dips1[i]]<prices1[dips1[i-1]] else  prices1[dips1[i-1]] )
        
        if(support <= superSupport):
            superSupport = min(prices1[dips1])
        
        print("support:",support,"superSupport:",superSupport)


        if(resistance > priceToday and priceToday > support):
            if(abs(resistance - priceToday) < diffCheck):
                return -1
            elif(abs(support - priceToday) < diffCheck):
                return 1
            return 0

        elif(resistance < priceToday):
            if(abs(superResistance - priceToday) < diffCheck):
                return -1
            elif(abs(resistance - priceToday) < diffCheck):
                return 1
            return 0

        elif(support > priceToday):
            if(abs(superSupport - priceToday) < diffCheck):
                return 1
            elif(abs(support - priceToday) < diffCheck):
                return -1
            return 0
        return 0