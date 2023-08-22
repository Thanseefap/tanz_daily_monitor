




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



  
##IC B BOT
bot = telebot.TeleBot('6321431603:AAFaI7P3Y8tqjjPPHslASkFcGkzBSkYD_n0')
LOGIN_OTP = 'login_otp'
SL_UPDATE = 'sl_update'




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
    item4 = types.InlineKeyboardButton('FIN', callback_data='FIN')
    markup.add(item1, item2, item4)
    
    bot.send_message(message.chat.id, 'Index Selection', reply_markup=markup)
     
    
@bot.message_handler(commands=['client'])
def client_select(message):
    # Create the main menu with nested commands
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('MAIN', callback_data='1')
    item2 = types.InlineKeyboardButton('SMALL', callback_data='2')
    item4 = types.InlineKeyboardButton('OTH', callback_data='3')
    markup.add(item1, item2, item4)
    
    bot.send_message(message.chat.id, 'Client Selection', reply_markup=markup)
     



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