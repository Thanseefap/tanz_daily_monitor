from login import shoonya
import tkinter as tk
from datetime import datetime


otp=input('Enter OTP:')
client=shoonya(twofa=otp)
api=client.login()
scrip=input('Enter the script name : ')
stop_loss=float(input('Enter the SL : '))


def Riskmanager(script,percent):
        margin=api.get_limits()
        used_margin=float(margin['marginused'])
        
        #script='BANK'
        df1=pd.DataFrame(api.get_positions())
        df1[['urmtom', 'rpnl','netqty','netavgprc']] = df1[['urmtom', 'rpnl','netqty','netavgprc']].apply(pd.to_numeric)
        df1['net']=df1['netqty']*df1['netavgprc']
        Net_credit=df1['net'].sum()*-1
        mtm=df1['urmtom'][df1['tsym'].str.contains(script)].sum()+df1['rpnl'][df1['tsym'].str.contains(script)].sum()
        #Getting total margin used
        margin=api.get_limits()
        used_margin=float(margin['marginused'])
        p=(mtm/used_margin)*100
        
        if p<percent:
            
            df=df1
            symbols=df[df['tsym'].str.contains(script)][df['netqty']!='0'][['tsym','netqty']]
            
            for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])>0:
                    action= 'S'
                else:
                    action='B'
                api.place_order(buy_or_sell=action
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=symp, 
                                    quantity=abs(int(symbols.iloc[i][1])), discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
         
        show=[p,mtm,percent,used_margin,Net_credit]
        return show
    





import time

def update_strategy_performance(scrip, stop_loss):
    # code to update the performance of the trading strategy
    show = Riskmanager(scrip, stop_loss)
    Net_credit = show[4]
    Net_PL = show[0]
    CURRENT = show[1]
    stop_loss = show[2]
    margin = show[3]
    sl_in_cash = stop_loss * (margin / 100)
    # Modify the code here to perform the necessary actions with the values, such as saving to a file or database.

def on_entry_button_click():
    # code to execute when the entry button is clicked
    print("entry button clicked")

def on_exit_button_click():
    # code to execute when the exit button is clicked
    print("exit button clicked")

def ATM_price():
    qRes = api.get_quotes('NSE', 'Nifty Fin Service')
    indexLtp = float(qRes['lp'])
    import math
    mod = int(indexLtp) % 100
    if mod < 50:
        atmStrike = int(math.floor(indexLtp / 100)) * 100
    else:
        atmStrike = int(math.ceil(indexLtp / 100)) * 100
    return atmStrike

def Position():
    ret = api.get_positions()
    mtm = 0
    pnl = 0
    for i in ret:
        mtm += float(i['urmtom'])
        pnl += float(i['rpnl'])
    day_m2m = mtm + pnl
    return day_m2m

while True:
    update_strategy_performance(scrip, stop_loss)
    time.sleep(10)  # Delay for 10 seconds


