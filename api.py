from neo_api_client import NeoAPI
from datetime import date, timedelta
import pandas as pd
import datetime
import calendar
import time
import json
import sys

# credentials
consumer_key = ''
consumer_secret = ''
mobile_number = ''
password = ''

def on_message(message):
    print(message)    
def on_error(error_message):
    print(error_message)
client = NeoAPI(consumer_key = consumer_key, consumer_secret = consumer_secret, 
                environment='prod', on_message=on_message, on_error=on_error, on_close=None, on_open=None)
client.login(mobilenumber = mobile_number, password = password)

otp = input("Enter OTP: ")
client.session_2fa(str(otp))
reuse_session = client.reuse_session
with open("creds.json","w") as file:
    file.write(json.dumps(reuse_session))

def get_ltp_index():
    ins_token = [{"instrument_token": "Nifty 50", "exchange_segment": "nse_cm"}]
    try:
        ltp = (client.quotes(instrument_tokens=ins_token, quote_type="ltp", isIndex=True))['message'][0]['last_traded_price']
        return round(float(ltp))
    except Exception as e:
        print("Exception when calling get Quote api->quotes: %s\n" % e)
        return -1

def log_text(message):
    today = datetime.datetime.now().date().strftime("%d_%m_%Y")
    filename = f'Text_Logs_{today}.txt'
    print(message)
    with open(filename, "a") as f:
        f.write(message + "\n")
    
offset = datetime.timedelta(hours=5, minutes=30)
column_names = ['Index','Timestamp', 'Spot']
csv_log = pd.DataFrame(columns=column_names)
i = 0

now = datetime.datetime.now()
tstamp = now + offset
tstamp = tstamp.strftime("%H:%M:%S")

while ((tstamp > "09:15:00") and (tstamp < "15:30:00")):
    now = datetime.datetime.now()
    tstamp = now + offset
    tstamp = tstamp.strftime("%H:%M:%S")

    temp = get_ltp_index()
    if (temp != -1):
        spot = temp
    elif (temp == -1):
        while (temp == -1):
            log_text(f"Error initializing Index!")
            with open("creds.json","r") as file:
                reuse_session = json.load(file)
            client = NeoAPI(access_token="test",environment="prod", reuse_session=reuse_session)
            temp = get_ltp_index()
            spot = temp

    log_text(f"{tstamp} | Fetched market price for Nifty 50 : {spot}")

    csv_log.loc[i, 'Index'] = i
    csv_log.loc[i, 'Timestamp'] = tstamp
    csv_log.loc[i, 'Spot'] = spot
    
    today = datetime.datetime.now().date().strftime("%d_%m_%Y")
    csv_log.to_csv(f'RawLogs_{today}.csv', index=False)
    i += 1
    time.sleep(1)
