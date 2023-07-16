
client=shoonya(twofa='648613',client_id='1')
api=client.login()


import pandas as pd
import sqlite3
from datetime import datetime


def strike_selection(indexLtp):
    import math
    mod = int(indexLtp)%100
    if mod < 50:
        openstrike =  int(math.floor(indexLtp / 100)) * 100
    else:
        openstrike=  int(math.ceil(indexLtp /100)) * 100
    return openstrike




def last_traded_price(t,e):
    ret = api.get_quotes(exchange=str(e), token=str(t))
    return float(ret['lp'])

def price_for_optionchain(df):
    return last_traded_price(df['token'],'NFO')

def place_order(action,symp,qty=1):
    
        x=api.place_order(buy_or_sell=action
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=symp, 
                                    quantity=qty*25, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_ic')
        time.sleep(1)
        if x['stat']=='Ok':
            ret = api.single_order_history(orderno=x['norenordno'])
            print(ret[0]['status'])
            #need to confirm the status for success order for valdidating condition
            if ret[0]['status']=='Rejected':
                
                time.sleep(1)
                result={'stat':  ret[0]['status'],'entry_price':float(ret[0]['prc'])}
                return result
              #  return  ret[0]['status'] #place_order(action,symp,qty=qty)
            else :
                result={'stat':  ret[0]['status'],'entry_price':ret[0]['prc']}
                return result
        
    

    
test=Iron_condor('BANK',api)  
