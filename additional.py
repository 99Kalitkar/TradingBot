import pandas as pd
from utils import MongoDB
def UpdateNseList():
    db = MongoDB()
    NSELIST = pd.read_csv('nseList.csv', sep=',', header=0)
    for i in range(len(NSELIST)):
        doc = {
            'Name': NSELIST['Name'][i],
            'Symbol': NSELIST['Symbol'][i]
        }
        db.InjectData('nseList',doc)