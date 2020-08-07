#  Loading necessary packages
from datetime import datetime, time, timedelta
import pandas as pd
import numpy as np
from os import path
import os

# Recording start time to check the overall execution time
startTime = datetime.utcnow()

# Reading nifty50 stocks data from moneycontrol website.
tables = pd.read_html("https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9")
niftyDF = tables[0]
niftyDF = niftyDF.drop(['Industry','Mkt Cap(Rs cr)'], axis=1)
stocksList = pd.read_csv("StockCodeList.csv")
niftyDF['Company Name'] = stocksList['StockCode']
del stocksList

# Check of Exclusion is exists, if yes : run the rule and update the Exclusion if any stock hits the rule
# else create the file.
rule1 = pd.DataFrame()
if path.isfile('ExclusionStocksList.csv'):
    # Rule 1 : if the stock movement is above 4% today
    niftyDF['Rule1'] = np.where(abs(niftyDF['%Chg']) >= 2, True, False)
    rule1 = niftyDF[niftyDF['Rule1'] == True]
    rule1 = rule1.drop(['Rule1'], axis=1)
    temp = pd.read_csv("ExclusionStocksList.csv")
    temp1 = temp[temp['Rule1'] == 1]
    rule1 = rule1[~ rule1['Company Name'].isin(temp1['StockCode'])]
    temp.loc[temp['StockCode'].isin(rule1['Company Name']), ['Rule1']] = 1
    temp.to_csv('ExclusionStocksList.csv', index=False)
    del [temp, temp1]
else:
    temp = pd.read_csv("StockCodeList.csv")
    temp["Rule1"] = ""
    temp.to_csv('ExclusionStocksList.csv', index=False)

# Send the Message
if not rule1.empty:
    messageText = rule1.to_string(index=False)
    # Sending custom messages to WhatsApp
    from twilio.rest import Client
    account_sid = 'AC35a406b81005930c30c6f2814affd7f0'
    auth_token = 'b047925fb7b21c24d4da0629f2b1f1ae'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=messageText,
        to='whatsapp:+917092814709'
    )
    print("done !!!!")


# Removing the Exclusion.csv to reset the rules for next day
if ((datetime.utcnow() + timedelta(hours=5, minutes=30)).time() < time(hour=9, minute=0)) or \
        ((datetime.utcnow() + timedelta(hours=5, minutes=30)).time() > time(hour=15, minute=30)):
    # os.remove('ExclusionStocksList.csv')
    print('cool!')


# Showing the overall execution time
elapsedTime = datetime.utcnow() - startTime
print(elapsedTime)