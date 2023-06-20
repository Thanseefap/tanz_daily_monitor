
global scrip
from NorenRestApiPy.NorenApi import  NorenApi
import logging
import requests
import json,os
import time,datetime
from time import sleep
import matplotlib.pyplot as plt
from io import BytesIO
import logging
from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler
from datetime import datetime





class shoonya(object):
      
    _root={"login": "/QuickAuth", "fund": "/Limits", "position": "/PositionBook", "orderbook": "/OrderBook", "tradebook": "/TradeBook", "holding": "/Holdings", 
             "order": '/PlaceOrder', "modifyorder": '/ModifyOrder', "cancelorder": '/CancelOrder', "exitorder": '/ExitSNOOrder', "singleorderhistory": '/SingleOrdHist',
             "searchscrip": '/SearchScrip', "scripinfo": '/GetSecurityInfo', "getquote": '/GetQuotes', "hist_data": "/TPSeries", "option": "/GetOptionChain"}
    

        

    #make the api call


    def __init__(self, twofa: str = None, client_id: str = None):
        if client_id=='1':
            self.uid = 'FA127352'
            self.pwd = 'Haya@2020'
            self.factor2 = twofa
            self.imei = '60-45-CB-C5-A7-49'
            self.app_key = 'a2e650f7d642a160d3d428f6795c0b20'
            self.vc = 'FA127352_U'
        elif client_id=='2':
            self.uid = 'FA92112'
            self.pwd = 'Tanz@2020'
            self.factor2 = twofa
            self.imei = '60-45-CB-C5-A7-49'
            self.app_key = '3314839374e9c76e933188930cef5bdd'
            #self.wss = None
            self.vc='FA92112_U'
        else:
            self.uid = 'FA76209'
            self.pwd = 'Strangle@24'
            self.factor2 = twofa
            self.imei = '60-45-CB-C5-A7-49'
            self.app_key = '6aa1e19981a9f1eeef8b2a96598ef3e3'
            #self.wss = None
            self.vc='FA76209_U'
                        

            
            

    def login(self):
           
            api = None
    
            class ShoonyaApiPy(NorenApi):
               def __init__(self):
                    NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
                    global api
                    api = self
            
            
       
         
        #enable dbug to see request and responses
            logging.basicConfig(level=logging.DEBUG)
            
            #start of our program
            api = ShoonyaApiPy()
        
            ret = api.login(userid=self.uid, password=self.pwd, twoFA=self.factor2, vendor_code=self.vc, api_secret=self.app_key, imei=self.imei)
            
            if ret is not None :   
                if ret['stat']=='Ok':
                    self.api = api
                    print("Logged In.")
                    return self.api
                else:
                    return f"Unable to Login. Reason:{res.text}"
            else:
                return 'login  error'
                print('login  error')
                    






## Thanseef



#function for exiting all position
## Function which will return the percentage profit and exit if it's greater than stop loss
def Riskmanager(script,percent):
        margin=api.get_limits()
        used_margin=float(margin['marginused'])
        try :
            
        #script='BANK'
            df1=pd.DataFrame(api.get_positions())
            if script=='ALL':
                df1=df1[df1['exch']=='NFO']
            else:
                df1=df1[df1['exch']=='NFO'][df1['tsym'].str.contains(script)]
            df1[['urmtom', 'rpnl','netqty','netavgprc']] = df1[['urmtom', 'rpnl','netqty','netavgprc']].apply(pd.to_numeric)
            df1['net']=df1['netqty']*df1['netavgprc']
            Net_credit=df1['net'].sum()*-1
            booked_pl=df1['rpnl'].sum()
            un_real_pl=df1['urmtom'].sum()
            mtm=booked_pl+un_real_pl
            #Getting total margin used
            margin=api.get_limits()
            used_margin=float(margin['marginused'])
            p=(mtm/used_margin)*100
        except AttributeError:
            show=['No']
            return show
        
        if p<percent:
            
            df=df1
            symbols=df[df['netqty']!=0][['tsym','netqty']]
            symbols.sort_values( by='netqty',
            ascending=False)
            
            for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])<0:
                    api.place_order(buy_or_sell='B'
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=symp, 
                                    quantity=abs(int(symbols.iloc[i][1])), discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
                else:
                    api.place_order(buy_or_sell='S'
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=symp, 
                                    quantity=abs(int(symbols.iloc[i][1])), discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
                
            show=['No']
            
            return show
         
        show=[p,mtm,percent,used_margin,Net_credit,booked_pl,un_real_pl]
        show= [ round(elem,2) for elem in show ]
        return show
        
        
def update_strategy_performance(script, stop_loss):
    # code to update the performance of the trading strategy
    show = Riskmanager(script, stop_loss)
    Net_credit = show[4]
    Net_PL = show[0]
    CURRENT = show[1]
    stop_loss = show[2]
    margin = show[3]
    sl_in_cash = stop_loss * (margin / 100)

    return show
    # Modify the code here to perform the necessary actions with the values, such as saving to a file or database.
     
                
                






