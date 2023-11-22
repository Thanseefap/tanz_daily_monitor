
global scrip
global api
global sl
global exit
global profit_b
global client_id
global expiry
global PNL_TYPE
global no_lot
global sl_type
global exchange


no_lot=1
scrip='ALL'
sl=-0.15
profit_b=1

client_id='7'
exit='NO'
expiry='NO'
PNL_TYPE='T_PNL'
sl_type='P'
exchange='NFO'


from math import floor
import re
from NorenRestApiPy.NorenApi import  NorenApi
import logging
import requests
import json,os
import time,datetime
from time import sleep
#import matplotlib.pyplot as plt
from io import BytesIO
import logging
#from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import telebot
import numpy as np
from tabulate import tabulate

import pandas as pd
from telebot import types
from login import shoonya
from datetime import datetime


## Main BOT 6277515369:AAET-z6EumKmJ2hgredC3akclYWrBdyG8n0
### Small Bot 6280168009:AAG1iX2uiRV4zTH-03QC73PgXqsU85dEAEA

        
  

bot = telebot.TeleBot('6280168009:AAG1iX2uiRV4zTH-03QC73PgXqsU85dEAEA')





## Thanseef


## Entry helper for re entry and initial enrty for exipry day

## strangle entry with hedge,




def nearest_strikes():
    
    
    strikes=[]     
    if scrip=='BANKNIFTY':
        qRes = api.get_quotes('NSE', 'Nifty Bank')
        spread=100
        lot=15
        index='BANKNIFTY'
    elif scrip=='FIN':
            qRes = api.get_quotes('NSE', 'Nifty Fin Service')
            lot=40
            spread=50
            index='FINNIFTY'
    elif scrip=='NIFTY': 
            qRes = api.get_quotes('NSE', 'Nifty 50')
            lot=50
            spread=50
            index='NIFTY'
    else:
        print('select index')
        return 'Not Possible : SCRIP NOT SELECTED'

    print(qRes)
    index_ltp=float(qRes['lp'])

    # Finding ATM Strike
    import math
    mod = float(index_ltp)%spread
    if mod < spread/2:
        atm_strike=int((index_ltp-mod))
    else:
        atm_strike=int(index_ltp-mod+spread)

    PUT_STRIKES=[]
    CALL_STRIKES=[]
    LEVELS=[]
    for i in range(15):
             PUT_STRIKES.append(atm_strike-spread*i)
             CALL_STRIKES.append(atm_strike+spread*i)
             LEVELS.append(int(i))
    data = {
    'LEVEL':LEVELS,
    'PUT': PUT_STRIKES,
    'CALL': CALL_STRIKES
     }

    # Create DataFrame from dictionary
    df = pd.DataFrame(data)
    df['PUT_NAME'] = df.apply(lambda row: f"{index}{expiry}P{row['PUT']}", axis=1)
    df['CALL_NAME'] = df.apply(lambda row: f"{index}{expiry}C{row['CALL']}", axis=1)
    
    return df



def place_order(BUY_SELL,sym,qty):
    if scrip=='BANKNIFTY':
        qRes = api.get_quotes('NSE', 'Nifty Bank')
        spread=100
        lot=15
        index='BANKNIFTY'
    elif scrip=='FIN':
            qRes = api.get_quotes('NSE', 'Nifty Fin Service')
            lot=40
            spread=50
            index='FINNIFTY'
    elif scrip=='NIFTY': 
            qRes = api.get_quotes('NSE', 'Nifty 50')
            lot=50
            spread=50
            index='NIFTY'
    else:
        print('select index')
        return 'Not Possible : SCRIP NOT SELECTED'
    test1=qty*lot
    print(test1)
    print(BUY_SELL,test1,sym)
    x=api.place_order(buy_or_sell=BUY_SELL
                                        , product_type='M',
                                            exchange=exchange, tradingsymbol=sym, 
                                            quantity=qty*lot, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                            retention='DAY', remarks='my_algo_order')   
    #This will return 'Ok' if order is processed to the system

    return x['stat']


def entry_expiry(level_otm,hedge_diff,entry_type,lot):
     #
     # finnding the level for the selected index
     df=nearest_strikes()
     #df[df['LEVEL']==1]
     
     level_otm=int(level_otm)
     print(df)
     print(type(level_otm))
    # print(df[[df['LEVEL']==level_otm]])
     sell_sym_c=df['CALL_NAME'][df['LEVEL']==level_otm].iloc[0]
     sell_sym_p=df['PUT_NAME'][df['LEVEL']==level_otm].iloc[0]
     buy_sym_c=df['CALL_NAME'][df['LEVEL']==(level_otm+hedge_diff)].iloc[0]
     buy_sym_p=df['PUT_NAME'][df['LEVEL']==(level_otm+hedge_diff)].iloc[0]
     
    
     if entry_type=='BOTH':
          
        place_order('B',buy_sym_c,lot)
        place_order('S',sell_sym_c,lot)

        place_order('B',buy_sym_p,lot)
        check=place_order('S',sell_sym_p,lot)

        if check=='Ok':
             return f"Entry Successfull PUT And CALL with  lot : {lot}, CALL :{sell_sym_c} & PUT : {sell_sym_p} and Hedge -- Call : {buy_sym_c} & Sell  : {buy_sym_p}"
     elif entry_type=='CALL':
        place_order('B',buy_sym_c,lot)
        check=place_order('S',sell_sym_c,lot)
        if check=='Ok':
             return f"Entry Successfull CALL with {lot}, CALL :{sell_sym_c} and Hedge -- Call : {buy_sym_c} "

     elif entry_type=='PUT':
        place_order('B',buy_sym_p,lot)
        check=place_order('S',sell_sym_p,lot)
        if check=='Ok':
             return f"Entry Successfull PUT with {lot}, PUT : {sell_sym_p} and Hedge -- Put : {buy_sym_p}"

     return 'Entry not succesful'



#function for exiting all position
## Function which will return the percentage profit and exit if it's greater than stop loss
#
#Adjustment Expiry
def adjustment(CALL_PUT,ACTION,LEVEL,QTY):
        try :
             
            if api is None:
                return 'Not Logged In'
        except NameError:
                return 'Not Logged In'
        LEVEL=int(LEVEL)
        df1=pd.DataFrame(api.get_positions())
        if scrip=='BANKNIFTY':
             qRes = api.get_quotes('NSE', 'Nifty Bank')
             spread=100
             lot=15
        elif scrip=='FIN':
             qRes = api.get_quotes('NSE', 'Nifty Fin Service')
             lot=40
             spread=50
        elif scrip=='NIFTY': 
             qRes = api.get_quotes('NSE', 'Nifty 50')
             lot=50
             spread=50
        else:
             return 'ADJ Not Possible : SCRIP NOT SELECTED'
        
        QTY=int(QTY)

        df1=df1[df1['exch']==exchange][df1['tsym'].str.contains(scrip)]
        if scrip=='NIFTY':
                     df1=df1[~df1['tsym'].str.contains('BANK')]
                     df1=df1[~df1['tsym'].str.contains('FIN')]

        df1[['symbol','expiry','Strike','CALL_PUT','err']]=df1['dname'].str.split(' ', expand=True)
        
        df1['current_strike']=qRes['lp']


        df1[['current_strike','Strike','urmtom', 'rpnl','netqty','netavgprc','lp']] = df1[['current_strike','Strike','urmtom', 'rpnl','netqty','netavgprc','lp']].apply(pd.to_numeric)
        
   
         #Defining CALL or PUT
        if CALL_PUT=='C':
          
            df1['DIFF']=df1['Strike']-df1['current_strike']
            df1=df1[df1['CALL_PUT']=='CE'][df1['netqty']<0]
            if ACTION=='+':
                 factor=-1*spread
            elif  ACTION=='-' :
                 factor=spread
            else:
                 factor=0


        else:
          
            df1['DIFF']=df1['current_strike']-df1['Strike']
            df1=df1[df1['CALL_PUT']=='PE'][df1['netqty']<0]
            if ACTION=='+':
                 factor=spread
            elif  ACTION=='-' :
                 factor=-1*spread
            else:
                 factor=0
        df1=df1.sort_values( by='DIFF') 

        # Defining Action that needs to be done

        

        tsym=df1['tsym'].iloc[LEVEL-1]
   
        
        x=api.place_order(buy_or_sell='B'
                                        , product_type='M',
                                            exchange=exchange, tradingsymbol=tsym, 
                                            quantity=QTY*lot, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                            retention='DAY', remarks='my_algo_order')
        if factor==0:
             return 'Reduced Position'+tsym
        if x['stat']=='Ok':
            tsym1=df1['symbol'].iloc[LEVEL-1]+df1['expiry'].iloc[LEVEL-1]+CALL_PUT+str(df1['Strike'].iloc[LEVEL-1]+factor)
        
            x=api.place_order(buy_or_sell='S'
                                        , product_type='M',
                                            exchange=exchange, tradingsymbol=tsym1, 
                                            quantity=QTY*lot, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                            retention='DAY', remarks='my_algo_order')
            if x['stat']=='Ok':
                return f"Adjustment of {QTY} on {tsym}, changed to  {tsym1} "
    










def Riskmanager(script,percent):
        
        margin=api.get_limits()
        used_margin=float(margin['marginused'])
        try :
            
        #script='BANK'
            df1=pd.DataFrame(api.get_positions())
            if script=='ALL':
                df1=df1[df1['exch']==exchange]
            else:
                print(script)
                print(df1)
                df1=df1[df1['tsym'].str.contains(script)]

                ## Taking care of NIFTY as BANKNIFTY contains NIFTY in tsym name
                if script=='NIFTY':
                     df1=df1[~df1['tsym'].str.contains('BANK')]
                     df1=df1[~df1['tsym'].str.contains('FIN')]
                ## Added Expiry
              #  print(expiry)
                if expiry !='NO':
                    df1=df1[df1['tsym'].str.contains(expiry)]
                    
            df1[['urmtom', 'rpnl','netqty','netavgprc','lp']] = df1[['urmtom', 'rpnl','netqty','netavgprc','lp']].apply(pd.to_numeric)
            df1['net']=df1['netqty']*df1['lp']
            Net_credit=df1['net'].sum()*-1

            booked_pl=df1['rpnl'].sum()
            un_real_pl=df1['urmtom'].sum()
            #print(df1['rpnl'])
            #print(df1['urmtom'])
            #print(booked_pl,un_real_pl)
            ## Ading PNL Selection method for 3PM Entry
            #print(PNL_TYPE)
            if PNL_TYPE=='T_PNL':
               mtm=booked_pl+un_real_pl
               print(mtm)
            else:
                mtm=un_real_pl
                print(mtm)
            #Getting total margin used
            margin=api.get_limits()
            used_margin=float(margin['marginused'])
            p=(mtm/used_margin)*100
            print('check 1')

            if script!='SEN':
                 filter_option='dname'
            else:
                 filter_option='tsym'
                 
            call_prem=-1*df1['net'][df1[filter_option].str.contains('CE')].sum()
            put_prem=-1*df1['net'][df1[filter_option].str.contains('PE')].sum()
            
            ce_b_lots=df1['netqty'][df1[filter_option].str.contains('CE')][df1['netqty']>0].sum()
            ce_s_lots=df1['netqty'][df1[filter_option].str.contains('CE')][df1['netqty']<0].sum()
            pe_b_lots=df1['netqty'][df1[filter_option].str.contains('PE')][df1['netqty']>0].sum()
            pe_s_lots=df1['netqty'][df1[filter_option].str.contains('PE')][df1['netqty']<0].sum()


            print(ce_b_lots,ce_s_lots,pe_b_lots,pe_s_lots)








        except AttributeError:
            show=['No-API Error']
            print('check 4')
            return show
        def exit_position(qty,sym,sell_buy):
             no_lot=abs(int(qty))/lot
             lot_multipier=8
             balance=no_lot%lot_multipier
             rep=floor(no_lot/lot_multipier)

             if rep>0:
                for i in range(rep):
                    
                    api.place_order(buy_or_sell=sell_buy
                                        , product_type='M',
                                            exchange=exchange, tradingsymbol=symp, 
                                            quantity=lot*lot_multipier, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                            retention='DAY', remarks='my_algo_order')
                    sleep(0.1)
                    
             if balance>0:
                  api.place_order(buy_or_sell=sell_buy
                                        , product_type='M',
                                            exchange=exchange, tradingsymbol=symp, 
                                            quantity=lot*balance, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                            retention='DAY', remarks='my_algo_order')
                  
                     
             
        df=df1
        symbols=df[df['netqty']!=0][['tsym','netqty']]
        symbols=symbols.sort_values( by='netqty')    # ascending=False


        if sl_type=='C':
             p=mtm
             print(p)
             
        if p<percent:
            print('check 3')
            for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])<0:
                    exit_position(symbols.iloc[i][1],symp,'B')
                else:
                    exit_position(symbols.iloc[i][1],symp,'S')
                
            show=['No-SL']
            
            return show
         
        elif p>=profit_b:
            # print('check 6')
             for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])<0:
                    exit_position(symbols.iloc[i][1],symp,'B')
                else:
                    exit_position(symbols.iloc[i][1],symp,'S')
                
             show=['No-Profit_booking']
            
             return show
        else:      
             show=[p,mtm,percent,used_margin,Net_credit,
                   booked_pl,un_real_pl,call_prem,ce_s_lots,ce_b_lots,put_prem,pe_s_lots,pe_b_lots]
             show= [ round(elem,2) for elem in show ]
             return show  
    
         
        
        
def update_strategy_performance(script, stop_loss):
    # code to update the performance of the trading strategy
    show = Riskmanager(script, stop_loss)
    print(show)
    if len(show)==1:
         return show
    Net_credit = show[4]
    Net_PL = show[0]
    CURRENT = show[1]
    stop_loss = show[2]
    margin = show[3]
    sl_in_cash = stop_loss * (margin / 100)

    return show
    # Modify the code here to perform the necessary actions with the values, such as saving to a file or database.
     

#6155748648:AAFpOUSJ51lWtMNMeWFztTVXjTcjgju-P64 Semiks bot

 
## Main BOT 6277515369:AAET-z6EumKmJ2hgredC3akclYWrBdyG8n0
### Small Bot 6280168009:AAG1iX2uiRV4zTH-03QC73PgXqsU85dEAEA





LOGIN_OTP = 'login_otp'
SL_UPDATE = 'sl_update'


# function to message the data as table 

def send_dataframe_as_table(chat_id, dataframe):
                        # Convert DataFrame to string with tabulate
                        table_string = tabulate(dataframe, headers='keys', tablefmt='fancy_grid')
                        table_string =table_string.replace('+', '＋').replace('-', '－').replace('|', '｜')
                        # Send the table string as a message
                        bot.send_message(chat_id, f'```\n{table_string}\n```', parse_mode='Markdown')


#logout method for logging out from API
@bot.message_handler(commands=['logout'])
def logout(message):
    ret = api.logout()
    if ret['stat']=='Ok':
        bot.send_message(message.chat.id, 'API Logged Out')
    else:
        bot.send_message(message.chat.id, 'API is unable to Logged Out')
                        


#end method stopping the RMS System
@bot.message_handler(commands=['end'])
def end(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton('Yes', callback_data='YES')
    item2 = types.InlineKeyboardButton('No', callback_data='NO')

    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, 'RMS Stop', reply_markup=markup)


 


@bot.message_handler(commands=['start'])
def start(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('Login Details', callback_data='Login Details')
    item2 = types.InlineKeyboardButton('Adjustment', callback_data='Adj')
    item4 = types.InlineKeyboardButton('Entry', callback_data='Entry')
    item3 = types.InlineKeyboardButton('RMS', callback_data='RMS')
    markup.add(item1, item2, item3, item4)
    try :
          api is None  
    except NameError:
          bot.send_message(message.chat.id, 'API Not connected')
    

    bot.send_message(message.chat.id, 'Main Menu', reply_markup=markup)
    
    
    
@bot.message_handler(commands=['index'])
def index_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('Portfolio', callback_data='Portfolio')
    item2 = types.InlineKeyboardButton('BANK', callback_data='BANK')
    item3 = types.InlineKeyboardButton('NIFTY', callback_data='NIFTY')
    item4 = types.InlineKeyboardButton('FIN', callback_data='FIN')
    item5 = types.InlineKeyboardButton('SENSEX', callback_data='SEN')
    markup.add(item1, item2, item3,item4,item5)
    
    bot.send_message(message.chat.id, 'Index Selection', reply_markup=markup)
     


@bot.message_handler(commands=['pnl_type'])
def pnl_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('TOTAL_PNL', callback_data='T_PNL')
    item2 = types.InlineKeyboardButton('CURRENT_PNL', callback_data='C_PNL')
    
    markup.add(item1, item2 )
    
    bot.send_message(message.chat.id, 'pnl Selection', reply_markup=markup)
     

@bot.message_handler(commands=['client'])
def client_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('MAIN', callback_data='1')
    item2 = types.InlineKeyboardButton('SMALL', callback_data='2')
    item4 = types.InlineKeyboardButton('MAIN_1', callback_data='7')
    markup.add(item1, item2, item4)
    
    bot.send_message(message.chat.id, 'Client Selection', reply_markup=markup)
     


@bot.message_handler(commands=['lot'])
def lot_select(message):
    bot.send_message(message.chat.id, 'Enter lot:')
    bot.register_next_step_handler(message, perform_lot)

def perform_lot(message):
    global no_lot
    

    
    chat_id = message.chat.id
    no_lot = int(message.text)
    
    bot.send_message(message.chat.id, f"Lot : {no_lot}")
    
    

# --------------expiry addition -------------#



@bot.message_handler(commands=['expiry'])
def expiry(message):
    df1=pd.DataFrame(api.get_positions())
    if df1.shape[0]==0:
         bot.send_message(message.chat.id, 'Enter expiry :DD-MMM-YY')
         bot.register_next_step_handler(message, perform_expiry)
    else:
            temp=[]
            
            for i in df1['token']:
                x=api.get_security_info(exchange, i)
                temp.append(x['exd'])
            y=set(temp)
            for  i  in y:
                bot.send_message(message.chat.id, i)

            bot.send_message(message.chat.id, 'Enter expiry :DD-MMM-YY')
            print(message)
            bot.register_next_step_handler(message, perform_expiry)

def perform_expiry(message):
    global expiry
    
    
    chat_id = message.chat.id
    x = message.text
    expiry =x.replace("-","")
   
    bot.send_message(message.chat.id, f"Set Exipry is {expiry}")


## Modfied SL 

@bot.message_handler(commands=['sl_type'])
def index_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('% SL', callback_data='SL-P')
    item2 = types.InlineKeyboardButton('CASH SL', callback_data='SL-C')
    
    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, 'SL Selection', reply_markup=markup)
     


@bot.message_handler(commands=['sl'])       
def sl_update(message):
    bot.send_message(message.chat.id, 'Enter SL:')
    bot.register_next_step_handler(message, update_sl)

def update_sl(message): 
    chat_id = message.chat.id
    global sl
    sl = float(message.text)
    bot.send_message(message.chat.id, f'SL has been set to {sl}')

# profit booking addition
@bot.message_handler(commands=['profit_booking'])       
def psl_update(message):
    bot.send_message(message.chat.id, 'Enter profit_booking % :')
    bot.register_next_step_handler(message, p_update_sl)

def p_update_sl(message): 
    chat_id = message.chat.id
    global profit_b
    profit_b = float(message.text)
    bot.send_message(message.chat.id, f'Profit booking has been set to {profit_b}')


@bot.message_handler(commands=['login'])
def login_shoonya(message):
    bot.send_message(message.chat.id, 'Enter OTP:')
    print(message)
    bot.register_next_step_handler(message, perform_login)

def perform_login(message):
    global api
    global exit
    global expiry
    

    expiry='NO'
    exit='NO'
    chat_id = message.chat.id
    otp = message.text
    client=shoonya(twofa=otp,client_id=client_id)
    api=client.login()

   
    if api is None:
         bot.send_message(message.chat.id, 'Login Failed')
    else:
         bot.send_message(message.chat.id, 'Login In')
    
    
    #bot.send_message(chat_id, 'Logged In')



    #bot.send_message(chat_id, 'Logged In')

@bot.callback_query_handler(func=lambda call: True )
def callback_handler(call):
    global scrip
    global exit
    global PNL_TYPE
    global lot
    global sl_type
    global exchange
    print(call.data)
    if call.data == 'Login Details':
    # Echo the user's message
                margin=api.get_limits()
                status=margin['stat']
                if status=='Ok':
                    cash_margin=margin['cash']
                    send_text=f'API Status : {status} & Cash Margin : {cash_margin}'
                    bot.send_message(call.message.chat.id, send_text)
                
                else:
                    bot.send_message(call.message.chat.id, f'API :  {status}')
                
            #else:
           #    bot.send_message(call.message.chat.id, 'Enter SL : ')
           #    chat_id = message.chat.id
          #    text = message.text
          #    global sl
          #    sl=float(text)
          #    print(sl)
          #    bot.send_message(call.message.chat.id, 'Set SL')
   #

    elif call.data=='Entry':
        
        markup = types.InlineKeyboardMarkup(row_width=4)

        item1 = types.InlineKeyboardButton('1', callback_data='LEV1')
        item2 = types.InlineKeyboardButton('2', callback_data='LEV2')
        item3 = types.InlineKeyboardButton('3', callback_data='LEV3')
        item4 = types.InlineKeyboardButton('4', callback_data='LEV4')
        item5 = types.InlineKeyboardButton('5', callback_data='LEV5')
        item6 = types.InlineKeyboardButton('6', callback_data='LEV6')
        item7 = types.InlineKeyboardButton('7', callback_data='LEV7')
        item8 = types.InlineKeyboardButton('8', callback_data='LEV8')
        markup.add(item1, item2, item3,item4,item5, item6, item7,item8)
        bot.send_message(call.message.chat.id, 'OTM LEVEL Selection', reply_markup=markup)
    elif call.data[:3]=='LEV': 

        markup = types.InlineKeyboardMarkup(row_width=4)

        QTY=call.data  
        bot.send_message(call.message.chat.id, call.data+' selected')
        print(QTY) 
        temp=['1','2','3','4','5','6','7','8']

        for i in temp:
            print(i)
            if i==QTY[-1]:
                item1 = types.InlineKeyboardButton('HED1', callback_data=i+'HED1')
                item2 = types.InlineKeyboardButton('HED2', callback_data=i+'HED2')
                item3 = types.InlineKeyboardButton('HED3', callback_data=i+'HED3')
                item4 = types.InlineKeyboardButton('HED4', callback_data=i+'HED4')
                item6 = types.InlineKeyboardButton('HED6', callback_data=i+'HED6')
                item10 = types.InlineKeyboardButton('HED10', callback_data=i+'HED10')
                item15 = types.InlineKeyboardButton('HED15', callback_data=i+'HED15')
                item20 = types.InlineKeyboardButton('HED20', callback_data=i+'HED20')
        
        markup.add(item1, item2, item3,item4, item6, item10,item15, item20)
        
        bot.send_message(call.message.chat.id, 'HEDGE Selection', reply_markup=markup)

    elif call.data[0:3]=='SL-':
        if call.data[3:]=='P':
            sl_type='P'

        else:
            sl_type='C'

  
    elif call.data[1:4]=='HED':
        markup = types.InlineKeyboardMarkup(row_width=2)
        qty=call.data[0]
        hedge=call.data[4:]
         
        item1 = types.InlineKeyboardButton('BOTH', callback_data='KITHNA'+qty+'B'+hedge)
        item2 = types.InlineKeyboardButton('CALL', callback_data='KITHNA'+qty+'C'+hedge)
        item3 = types.InlineKeyboardButton('PUT', callback_data='KITHNA'+qty+'P'+hedge)

        markup.add(item1, item2, item3)
        
        bot.send_message(call.message.chat.id, 'Entry Selection', reply_markup=markup)

    elif call.data[0:6]=='KITHNA':
        
        lev=int(call.data[6])
        
        if call.data[7]=='B':
             entry_type='BOTH'
        elif call.data[7]=='C':
             entry_type='CALL'
        else:
             entry_type='PUT'
        hedge=int(call.data[8:])
        
        print(lev,hedge)
        print(type(lev))
        print(type(hedge))
        status=entry_expiry(int(lev),int(hedge),entry_type,no_lot)
      #  bot.send_message(call.message.chat.id, status, reply_markup=markup)
        bot.send_message(call.message.chat.id, status)
    elif call.data=='Adj':
        markup = types.InlineKeyboardMarkup(row_width=4)

        item1 = types.InlineKeyboardButton('1', callback_data='VOL1')
        item2 = types.InlineKeyboardButton('2', callback_data='VOL2')
        item3 = types.InlineKeyboardButton('3', callback_data='VOL3')
        item77 = types.InlineKeyboardButton('4', callback_data='VOL4')

        markup.add(item1, item2, item3,item77)
     #   bot.send_message(call.message.chat.id, 'ADJ QTY Selection', reply_markup=markup)
    elif call.data[:3]=='VOL':
        markup = types.InlineKeyboardMarkup(row_width=4)

        QTY=call.data  
        bot.send_message(call.message.chat.id, call.data+' selected')
        print(QTY) 
        temp=['1','2','3','4']
        for i in temp:
            print(i)
            if i==QTY[-1]:
                item1 = types.InlineKeyboardButton('A|+C1', callback_data='ADJ|+C1'+i)
                item2 = types.InlineKeyboardButton('A|+C2', callback_data='ADJ|+C2'+i)
                item3 = types.InlineKeyboardButton('A|+C3', callback_data='ADJ|+C3'+i)
                item77 = types.InlineKeyboardButton('A|+C4', callback_data='ADJ|+C4'+i)

                item4 = types.InlineKeyboardButton('A|-C1', callback_data='ADJ|-C1'+i)
                item5 = types.InlineKeyboardButton('A|-C2', callback_data='ADJ|-C2'+i)
                item6 = types.InlineKeyboardButton('A|-C3', callback_data='ADJ|-C3'+i)
                item7 = types.InlineKeyboardButton('A|-C4', callback_data='ADJ|-C4'+i)

                item8 = types.InlineKeyboardButton('A|+P1', callback_data='ADJ|+P1'+i)
                item9 = types.InlineKeyboardButton('A|+P2', callback_data='ADJ|+P2'+i)
                item11 = types.InlineKeyboardButton('A|+P3', callback_data='ADJ|+P3'+i)
                item22 = types.InlineKeyboardButton('A|+P4', callback_data='ADJ|+P4'+i)

                item33 = types.InlineKeyboardButton('A|-P1', callback_data='ADJ|-P1'+i)
                item44 = types.InlineKeyboardButton('A|-P2', callback_data='ADJ|-P2'+i)
                item55 = types.InlineKeyboardButton('A|-P3', callback_data='ADJ|-P3'+i)
                item66= types.InlineKeyboardButton('A|-P4', callback_data='ADJ|-P4'+i)

        markup.add(item1, item2, item3,item77,item4, item5, item6,item7, item8, item9,item11, item22, item33,item44, item55, item66)
        
        bot.send_message(call.message.chat.id, 'Adj Selection', reply_markup=markup)
        

    
         
         

    elif call.data=='1':
    
        #global scrip
        client_id='1'
        bot.send_message(call.message.chat.id, 'Client: RMS Main')
        
    elif call.data=='2':
        #global scrip
        client_id='2'
        bot.send_message(call.message.chat.id, 'Index: RMS Small')

    elif call.data=='7':
        #global scrip
        client_id='7'
        bot.send_message(call.message.chat.id, 'Index: RMS New MAIN')

    elif call.data=='T_PNL':
        #global PNL_TYPE
        PNL_TYPE='T_PNL'
        bot.send_message(call.message.chat.id, 'PNL: Based on Total PNL')
        
    elif call.data=='C_PNL':
        #global PNL_TYPE
        PNL_TYPE='C_PNL'
        bot.send_message(call.message.chat.id, 'PNL: Based on Current PNL')
        
    elif call.data=='YES':
        #global scrip
        exit='YES'
        bot.send_message(call.message.chat.id, 'RMS STOPPING')
    elif call.data=='NO':
        #global scrip
        exit='NO'
        bot.send_message(call.message.chat.id, 'RMS Restart') 

    elif call.data=='Portfolio':
        #global scrip
        scrip='ALL'
        bot.send_message(call.message.chat.id, 'Index: Portfolio')
    elif call.data=='NIFTY':
        #global scrip
        scrip='NIFTY'
        lot=50
        bot.send_message(call.message.chat.id, 'Index: NIFTY')
    elif call.data=='FIN':
        #global scrip
        scrip='FIN'
        lot=40
        bot.send_message(call.message.chat.id, 'Index: FIN')
    elif call.data=='BANK':
        #global scrip
        scrip='BANKNIFTY'
        lot=15
        bot.send_message(call.message.chat.id, 'Index: BANK NIFTY')

    elif call.data=='SEN':
        #global scrip
        scrip='SEN'
        lot=10
        exchange='BFO'
        bot.send_message(call.message.chat.id, 'Index: SENSEX')
        
    elif call.data=='Profit Booking':
        df1=pd.DataFrame(api.get_positions())
        if df1.shape[0]==0:
            bot.send_message(call.message.chat.id, 'There is No Position ')
        else:
            df1=df1[df1['exch']==exchange][df1['netqty']!='0']
          
        df1['CALL_PUT'] = np.where(df1['tsym'].str.contains('C', 'CE',
                                    'PE'))
        df1[['tsym','lp','CALL_PUT']]
        ce=df1[df1['CALL_PUT']=='CE'][df1['lp']==df['lp'].max()].iloc[0][0]
        pe=df1[df1['CALL_PUT']=='PE'][df1['lp']==df['lp'].max()].iloc[0][0]
       
        api.place_order(buy_or_sell='B'
                                , product_type='M',
                                    exchange=exchange, tradingsymbol=ce, 
                                    quantity=lot, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
        api.place_order(buy_or_sell='B'
                                , product_type='M',
                                    exchange=exchange, tradingsymbol=pe, 
                                    quantity=lot, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
            
        bot.send_message(call.message.chat.id, 'Reduced Risk / Profit Booked by 1 lot')

    elif call.data=='POS':
         df1=pd.DataFrame(api.get_positions())
         send_dataframe_as_table(call.message.chat.id,df1)
    elif call.data=='Position':
        
            df1=pd.DataFrame(api.get_positions())
            if df1.shape[0]==0:
                bot.send_message(call.message.chat.id, 'There is No Position ')
                if exit==0:
                     bot.send_message(call.message.chat.id, f'RMS - Not on run, fixed SL  :{sl} and Index : {scrip}')
                else: 
                     bot.send_message(call.message.chat.id, f'RMS - Running with fixed SL as : {sl} and Index : {scrip}')
                
            else:
                
                df1=df1[df1['exch']==exchange][df1['netqty']!='0']
                df1[['urmtom', 'rpnl','netqty','netavgprc']] = df1[['urmtom', 'rpnl','netqty','netavgprc']].apply(pd.to_numeric)
                df1['Buy_Sell'] = np.where(df1['netqty']>0, 'BUY',
                                   np.where(df1['netqty']<0, 'SELL','Other'
                                    ))
                df1['Instrument'] = np.where(df1['tsym'].str.contains('BANK'), 'BANKNIFTY',
                                   np.where(df1['tsym'].str.contains('FIN'), 'FINNIFTY',
                                    'Stock'))
                df1=df1[['Instrument','Buy_Sell','netqty','urmtom','rpnl']]
                
                grouped = df1.groupby(['Instrument','Buy_Sell']).sum()
                grouped[['Instrument', 'Buy_Sell']]=grouped.index
                #send_dataframe_as_table(call.message.chat.id, grouped)
                
                
                if exit==0:
                     bot.send_message(call.message.chat.id, f'RMS - Not on run, fixed SL  :{sl} and Index : {scrip}')
                else: 
                     bot.send_message(call.message.chat.id, f'RMS - Running with fixed SL as : {sl} and Index : {scrip}')
                
            
    #elif call.data == 'API Health':
    #   margin=api.get_limits()
    #   
    #   send='API Response: Status' + margin['stat']+'& the'+'cash used '+ margin['cash']
    #   bot.send_message(call.message.chat.id, send)
    #   return
    
    
    elif call.data[:4]=='ADJ|':
         
         x=call.data
         LEVEL=x[-2]
         CALL_PUT=x[-3]
         ACTION=x[-4]
         QTY=x[-1]
         result=adjustment(CALL_PUT,ACTION,LEVEL,QTY)
         bot.send_message(call.message.chat.id, result)   




    elif call.data == 'RMS':
        # Create the submenu with nested commands
        submenu_markup = types.InlineKeyboardMarkup(row_width=2)
        submenu_item1 = types.InlineKeyboardButton('START_RMS', callback_data='SHOW_KPI')
        submenu_item2 = types.InlineKeyboardButton('KPI', callback_data='KPI')
        submenu_item3 = types.InlineKeyboardButton('Update_SL', callback_data='Update_SL')
      #  submenu_item4 = types.InlineKeyboardButton('index', callback_data='RMS')
        submenu_markup.add( submenu_item1,  submenu_item2,  submenu_item3)
    
        bot.send_message(call.message.chat.id, 'Main Menu', reply_markup=submenu_markup)
       
    ## make changesin th shpw kpi for taking scrip along with operation       
    elif call.data=='SHOW_KPI':
 #        bot.send_message(call.message.chat.id, 'Show KPI')
# Script setting up for the code
        
        while True:
            if call.data!='SHOW_KPI':
                 break
            print(exit)
            if exit=='YES':
                          break
            #if call.data=='Pause RMS':
            #    bot.send_message(call.message.chat.id, 'Pause RMS System as per Requirement')
             #   exit='YES'
            #    break
            #except requests.exceptions.ConnectionError as e:
            #except requests.exceptions.ConnectionError as e:
            show=update_strategy_performance(scrip, sl)
            if len(show)==1:
                
                bot.send_message(call.message.chat.id, 'Position Started Exiting')
                bot.send_message(call.message.chat.id,show[0])
                ret = api.get_order_book()

                for i in ret['norenordno'][ret['status']=='OPEN']:
                    x=api.cancel_order(orderno=i)
                    
                exit='YES'
                break    
             
            else:
                Net_credit = show[4]
                Net_PL = show[0]
                CURRENT = show[1]
                stop_loss = show[2]
                margin = round(show[3]/100000)
                sl_in_cash = round(stop_loss * (margin *100000/ 100),2)
                call_prem=show[7]
                call_s_lot=show[8]
                call_b_lot=show[9]
                put_prem=show[10]
                put_s_lot=show[11]
                put_b_lot=show[12]
               
                
      
                
                            
                data = {
                    'RMS Vaues': ['Fixed SL | Margin', '% P/L | Net Profit ', 'Profit Book % | Cash','Net Credit','SL in Cash','Booked PL','Un realised PL','CE Prem |  S  | B Lot','PE Prem | S | B Lot'],
                    'Values': [f"{stop_loss} | {margin} in lac",f"{Net_PL} | {CURRENT}",f"{profit_b} | {int(profit_b*margin*1000)}",Net_credit,sl_in_cash,show[5],show[6],f"{call_prem} | {call_s_lot} | {call_b_lot}",f"{put_prem} | {put_s_lot} | {put_b_lot}"]
                     
                }
                # Create a DataFrame from the dictionary
                df = pd.DataFrame(data)
                send_dataframe_as_table(call.message.chat.id,df)
               # send_dataframe_as_table(call.message.chat.id, df)
                #bot.send_message(call.message.chat.id, 'Set Stop Loss :' +str(stop_loss)+'& Net P/L : '+str(Net_PL)+'  & Net Credit Amount = '+str(Net_credit))
                time.sleep(20)  # Delay for 15 seconds
           #print('checker1')
           # if exit=='0':
            #    break
        if exit=='0':
                bot.send_message(call.message.chat.id, 'RMS Stopped with Exiting the Position')
        
                              
    
bot.infinity_polling(timeout=15, long_polling_timeout = 15)
