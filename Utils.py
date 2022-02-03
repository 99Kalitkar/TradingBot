import smtplib
import pandas as pd
from os import getcwd
import credentials as creds
from selenium import webdriver
from pymongo import MongoClient
from email.mime.text import MIMEText
from pandas.core.frame import DataFrame
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ChromeWebDriver:
    def __init__(self) -> None:
        chromeOptions = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": getcwd(), 
            "directory_upgrade": True
            }        
        chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)

class MongoDB:
    def __init__(self) -> None:
        client = MongoClient("mongodb+srv://tradingUser:" + creds.MONGO_PASS + "@masterdb.natd1.mongodb.net/TradingBot?retryWrites=true&w=majority")
        self.db = client.TradingBot
    
    def InjectData(self, collectionName: str, document: dict or list) -> bool:
        collection = self.db[collectionName]
        try:
            if(type(document) == dict):
                if(not collection.find_one(document)):
                    collection.insert_one(document)
            elif(type(document) == list):
                for doc in document:
                    if(not collection.find_one(doc)):
                        print(doc)
                        collection.insert_one(doc)
            return True
        except Exception as e:
            print(str(e))
            return False

    def RetriveData(self, collectionName: str, filter: dict = {}) -> DataFrame or None:
        collection = self.db[collectionName]
        cursor = collection.find(filter)
        data = []
        if(cursor):
            for row in cursor:
                data.append(row)
            data = pd.DataFrame(data)
            data = data.drop(['_id'], axis=1)
            return data
        return None

class Email:
    def __init__(self) -> None:
        self.session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        self.session.starttls() #enable security
        self.session.login(creds.EMAIL_USER, creds.EMAIL_PASS) #login with mail_id and password
        
    def SendEmail(self, email: list or str, predictions: list) -> None:
        template ='&nbsp;&nbsp;&nbsp;&nbsp;<p style="font-size: 18px;">{stockName}({stockSymbol})</p></br>'
        toBuy = '<h4>Stocks to Buy:</h4></br>'
        toSell = '<h4>Stocks to Sell:</h4></br>'
        doNothing = '<h4>Stocks do Nothing:</h4></br>'
        for row in predictions:
            if(row[2] == 1):
                toBuy += template.format(stockName = row[0], stockSymbol = row[1])
            elif(row[2] == -1):
                toSell += template.format(stockName = row[0], stockSymbol = row[1])
            else:
                doNothing += template.format(stockName = row[0], stockSymbol = row[1])
        mail_content = toBuy + toSell + doNothing
        message = MIMEMultipart()
        if(type(email) == str):
            message['From'] = creds.EMAIL_USER
            message['To'] = email
            message['Subject'] = 'Todays Prediction'   
            message.attach(MIMEText(mail_content, 'plain'))
            text = message.as_string()
            try:
                self.session.sendmail(creds.EMAIL_USER, email, text)
                return True
            except:
                return False
        elif(type(email) == list):
            for emailID in email:
                message['From'] = creds.EMAIL_USER
                message['To'] = emailID
                message['Subject'] = 'Todays Prediction'   
                message.attach(MIMEText(mail_content, 'plain'))
                text = message.as_string()
                try:
                    self.session.sendmail(creds.EMAIL_USER, emailID, text)
                except:
                    return False
            return True
        return False

