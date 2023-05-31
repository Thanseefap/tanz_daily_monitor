
from NorenRestApiPy.NorenApi import  NorenApi
import logging
import requests
import json,os
import time,datetime
from time import sleep


class shoonya(object):
      
    _root={"login": "/QuickAuth", "fund": "/Limits", "position": "/PositionBook", "orderbook": "/OrderBook", "tradebook": "/TradeBook", "holding": "/Holdings", 
             "order": '/PlaceOrder', "modifyorder": '/ModifyOrder', "cancelorder": '/CancelOrder', "exitorder": '/ExitSNOOrder', "singleorderhistory": '/SingleOrdHist',
             "searchscrip": '/SearchScrip', "scripinfo": '/GetSecurityInfo', "getquote": '/GetQuotes', "hist_data": "/TPSeries", "option": "/GetOptionChain"}
    

        

    #make the api call


    def __init__(self, twofa: str=None):
            self.uid = 'FA127352'
            self.pwd = 'Haya@2020'
            self.factor2 = twofa
            self.imei = '60-45-CB-C5-A7-49'
            self.app_key = 'a2e650f7d642a160d3d428f6795c0b20'
            #self.wss = None
            self.vc='FA127352_U'
            

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
                    print(f"Unable to Login. Reason:{res.text}")
                    return
            else:
                  print('login  error')
