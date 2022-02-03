from algos import *
from stocks import *
from utils import *
stock_Info = StocksInfo()
indicate = Indicators()
pattern = Patterns()
def prediction(stocks: list) -> None:
    columns = ['StockName', 'StockSymbol', 'DEMA', 'BBands', 'MACD', 'RSI', 'Zia', 'Marubozu', 'Engulfing', 
    'Hammer', 'ShootingStar', 'Harami', 'MorningStar', 'EveningStar', 'DowTheory', 'SandR',"Prediction", "Predication Percent"]
    stocksAnalysis = []
    for stock in stocks:
        try:
            symbol = stock_Info.GetStockSymbol(stock)
            print("StockName:", stock, "Symbol:", symbol)
            data = stock_Info.GetHistoricalData(symbol,'6mo','1d')
            analysisOutcome = [stock,symbol,
                indicate.DEMA(data['Close']),
                indicate.BBands(data['Close']),
                indicate.MACD(data['Close']),
                indicate.RSI(data['Close']),
                indicate.Zia(symbol),
                pattern.Marubozu(data),
                pattern.Engulfing(data),
                pattern.Hammer(data),
                pattern.ShootingStar(data),
                pattern.Harami(data),
                pattern.MorningStar(data),
                pattern.EveningStar(data),
                pattern.DowTheory(data['Close']),
                pattern.SandR1(data['Close'],60)
            ]
            
            b = 0
            s = 0
            for outcome in analysisOutcome[2:]:
                if(outcome==1):
                    b+=1
                elif(outcome==-1):
                    s+=1
            perBuy = b/(b+s)*100
            if(perBuy>70.0):
                analysisOutcome.append(1)
                print("Algo predicts to Buy with", perBuy, "%")
            elif(perBuy<40.0):
                analysisOutcome.append(-1)
                print("Algo Pridicts to Sell", perBuy, "%")
            else: 
                analysisOutcome.append(0)
                print("Algo Pridicts to Stayput", perBuy, "%")
            analysisOutcome.append(perBuy)
            stocksAnalysis.append(analysisOutcome)
        except Exception as e:
            print("Exception", e)

    pd.DataFrame(stocksAnalysis,columns=columns).to_csv("prediction.csv")


StocksToCheck = ['Adani Power', 'Arvind Limited', 'irctc', 'Laurus Lab', 
    "MCX","Power Finanace Corporation","IIFL SEC","JK Paper","Jubilant Ingrevia",
    "Advanced Enzyme Technologies","Sudarshan Chemical Industries","CSB Bank ",
    "Bajaj Consumer Care ","Castrol India ","CreditAccess Grameen ",
    "Aster DM Healthcare ","Banco Products ","Shalby ",
    "Nava Bharat Ventures","NCL Industries ","Mahindra CIE Automotive ",
    "Sandhar Technologies ","HSIL ","GM Breweries ",'paytm', 'Sms Pharmaceuticals',
    'burgerking', 'cchhl', 'Lemon tree', 'Nagafert', 'rpower', 'tatapower', 
    'tatamotors', 'TV18 broadcast', 'infy' ]
    
# StocksToCheck = ['tatapower']
prediction(StocksToCheck)
#     symbol = stock_Info.GetStockSymbol(stock)
#     print("StockName:", stock, "Symbol:", symbol)
#     data = stock_Info.GetHistoricalData(symbol,'6mo','1d')
#     print("prediction",pattern.SandR1(data['Close'],60))
#     # break

