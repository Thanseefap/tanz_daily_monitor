
global scrip
global api
global sl
global exit
global profit_b
global client_id
global expiry


scrip='ALL'
sl=-0.5
profit_b=1
client_id='2'
exit='NO'

from NorenRestApiPy.NorenApi import  NorenApi
import logging
import requests
import json,os
import time,datetime
from time import sleep
#import matplotlib.pyplot as plt
from io import BytesIO
import logging
from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import telebot
import numpy as np
from tabulate import tabulate

import pandas as pd
from telebot import types
from login import shoonya
from datetime import datetime



        
  






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
                ## Added Expiry
                df1=df1[df1['exch']=='NFO'][df1['tsym'].str.contains(expiry)]
                    
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
            print('check 1')
            call_profit=-1*df1['net'][df1['tsym'].str.contains('C')].sum()
            put_profit=-1*df1['net'][df1['tsym'].str.contains('P')].sum()
            print('check 2')
            ce_lots=len(df1['net'][df1['tsym'].str.contains('C')])
            pe_lots=len(df1['net'][df1['tsym'].str.contains('P')])


        except AttributeError:
            show=['No']
            print('check 4')
            return show
        def exit_position(qty,sym,sell_buy):
             api.place_order(buy_or_sell=sell_buy
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=symp, 
                                    quantity=abs(int(qty)), discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
             
        df=df1
        symbols=df[df['netqty']!=0][['tsym','netqty']]
        symbols=symbols.sort_values( by='netqty')    # ascending=False
        if p<percent:
            print('check 3')
            for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])<0:
                    exit_position(symbols.iloc[i][1],symp,'B')
                else:
                    exit_position(symbols.iloc[i][1],symp,'S')
                
            show=['No']
            
            return show
         
        elif p>=profit_b:
             print('check 6')
             for i in range(len(symbols)):
                symp=symbols.iloc[i][0]
                if float(symbols.iloc[i][1])<0:
                    exit_position(symbols.iloc[i][1],symp,'B')
                else:
                    exit_position(symbols.iloc[i][1],symp,'S')
                
             show=['No']
            
             return show
        else:
             show=[p,mtm,percent,used_margin,Net_credit,booked_pl,un_real_pl,call_profit,put_profit,ce_lots,pe_lots]
             show= [ round(elem,2) for elem in show ]
             return show  
    
         
        
        
def update_strategy_performance(script, stop_loss):
    # code to update the performance of the trading strategy
    show = Riskmanager(script, stop_loss)
    print(show)
    Net_credit = show[4]
    Net_PL = show[0]
    CURRENT = show[1]
    stop_loss = show[2]
    margin = show[3]
    sl_in_cash = stop_loss * (margin / 100)

    return show
    # Modify the code here to perform the necessary actions with the values, such as saving to a file or database.
     



 

### Small Bot

bot = telebot.TeleBot('6277515369:AAET-z6EumKmJ2hgredC3akclYWrBdyG8n0')
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
    item2 = types.InlineKeyboardButton('Holding', callback_data='Profit Booking')
    item4 = types.InlineKeyboardButton('Position', callback_data='Position')
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
    markup.add(item1, item2, item3,item4)
    
    bot.send_message(message.chat.id, 'Index Selection', reply_markup=markup)
     
    
@bot.message_handler(commands=['client'])
def client_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('MAIN', callback_data='1')
    item2 = types.InlineKeyboardButton('SMALL', callback_data='2')
    item4 = types.InlineKeyboardButton('MAIN_1', callback_data='7')
    markup.add(item1, item2, item4)
    
    bot.send_message(message.chat.id, 'Client Selection', reply_markup=markup)
     


# --------------expiry addition -------------#


@bot.message_handler(commands=['expiry'])
def expiry(message):
    df1=pd.DataFrame(api.get_positions())
    temp=[]
    for i in df1['token']:
        x=api.get_security_info('NFO', i)
        temp.append(x['exd'])
    y=set(temp)
    for  i  in y:
        bot.send_message(message.chat.id, i)

    bot.send_message(message.chat.id, 'Enter expiry :')
    print(message)
    bot.register_next_step_handler(message, perform_expiry)

def perform_expiry(message):
    global expiry
    
    
    chat_id = message.chat.id
    x = message.text
    expiry =x.replace("-","")
   
    bot.send_message(message.chat.id, f"Set Exipry is {expiry}")

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
    exit='NO'
    chat_id = message.chat.id
    otp = message.text
    client=shoonya(twofa=otp,client_id=client_id)
    api=client.login()
    print(api)
    if type(api)==str:
           bot.send_message(message.chat.id, api)
    else:
           bot.send_message(message.chat.id, 'Logged In')
    
    
    #bot.send_message(chat_id, 'Logged In')

@bot.callback_query_handler(func=lambda call: True )
def callback_handler(call):
    global scrip
    global exit
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
        bot.send_message(call.message.chat.id, 'Index: NIFTY')
    elif call.data=='FIN':
        #global scrip
        scrip='FIN'
        bot.send_message(call.message.chat.id, 'Index: FIN')
    elif call.data=='BANK':
        #global scrip
        scrip='BANK'
        bot.send_message(call.message.chat.id, 'Index: BANK NIFTY')
        
    elif call.data=='Profit Booking':
        df1=pd.DataFrame(api.get_positions())
        if df1.shape[0]==0:
            bot.send_message(call.message.chat.id, 'There is No Position ')
        else:
            df1=df1[df1['exch']=='NFO'][df1['netqty']!='0']
          
        df1['CALL_PUT'] = np.where(df1['tsym'].str.contains('C', 'CE',
                                    'PE'))
        df1[['tsym','lp','CALL_PUT']]
        ce=df1[df1['CALL_PUT']=='CE'][df1['lp']==df['lp'].max()].iloc[0][0]
        pe=df1[df1['CALL_PUT']=='PE'][df1['lp']==df['lp'].max()].iloc[0][0]
        if scrip=='BANK':
            quantity=25
        else:
            quantity=40
        api.place_order(buy_or_sell='B'
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=ce, 
                                    quantity=quantity, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
        api.place_order(buy_or_sell='B'
                                , product_type='M',
                                    exchange='NFO', tradingsymbol=pe, 
                                    quantity=quantity, discloseqty=0,price_type='MKT', #price=0.1,# trigger_price=199.50,
                                    retention='DAY', remarks='my_algo_order')
            
        bot.send_message(call.message.chat.id, 'Reduced Risk / Profit Booked by 1 lot')
    elif call.data=='Position':
        
            df1=pd.DataFrame(api.get_positions())
            if df1.shape[0]==0:
                bot.send_message(call.message.chat.id, 'There is No Position ')
                if exit==0:
                     bot.send_message(call.message.chat.id, f'RMS - Not on run, fixed SL  :{sl} and Index : {scrip}')
                else: 
                     bot.send_message(call.message.chat.id, f'RMS - Running with fixed SL as : {sl} and Index : {scrip}')
                
            else:
                
                df1=df1[df1['exch']=='NFO'][df1['netqty']!='0']
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
    elif call.data == 'RMS':
        # Create the submenu with nested commands
        submenu_markup = types.InlineKeyboardMarkup(row_width=2)
        submenu_item1 = types.InlineKeyboardButton('SHOW_KPI', callback_data='SHOW_KPI')
        submenu_item2 = types.InlineKeyboardButton('Position', callback_data='Position')
        submenu_item3 = types.InlineKeyboardButton('Update_SL', callback_data='Update_SL')
      #  submenu_item4 = types.InlineKeyboardButton('index', callback_data='RMS')
        submenu_markup.add( submenu_item1,  submenu_item2,  submenu_item3)
    
        bot.send_message(call.message.chat.id, 'Main Menu', reply_markup=submenu_markup)
       
    ## make changesin th shpw kpi for taking scrip along with operation       
    elif call.data=='SHOW_KPI':
 #        bot.send_message(call.message.chat.id, 'Show KPI')
# Script setting up for the code
        
        while True:
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
            if show[0]=='No':
                
                bot.send_message(call.message.chat.id, 'Position Started Exiting')
                
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
                call_profit=show[7]
                put_profit=show[8]
                ce_lots=show[9]
                pe_lots=show[10]
      
                
                            
                data = {
                    'RMS Vaues': ['Fixed SL | Margin', '% P/L | Profit Book % ', 'Net Profit','Net Credit','SL in Cash','Booked PL','Un realised PL','CE Prem | Lot','PE Prem | Lot'],
                    'Values': [f"{stop_loss} | {margin} in lac",f"{Net_PL} | {profit_b}",CURRENT,Net_credit,sl_in_cash,show[5],show[6],f"{call_profit} | {ce_lots}",f"{put_profit} | {pe_lots}"]
                     
                }
                # Create a DataFrame from the dictionary
                df = pd.DataFrame(data)
                send_dataframe_as_table(call.message.chat.id,df)
               # send_dataframe_as_table(call.message.chat.id, df)
                #bot.send_message(call.message.chat.id, 'Set Stop Loss :' +str(stop_loss)+'& Net P/L : '+str(Net_PL)+'  & Net Credit Amount = '+str(Net_credit))
                time.sleep(15)  # Delay for 15 seconds
           #print('checker1')
           # if exit=='0':
            #    break
        if exit=='0':
                bot.send_message(call.message.chat.id, 'RMS Stopped with Exiting the Position')
        
                              
    
bot.infinity_polling(timeout=10, long_polling_timeout = 5)
