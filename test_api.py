from login import shoonya
import tk
from datetime import datetime


otp=input('Enter OTP:')
client=shoonya(twofa=otp)
api=client.login()

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
    





scrip=input('Enter the script name')
stop_loss=float(input('Enter the SL'))

def update_strategy_performance():
    # code to update the performance of the trading strategy
    show=Riskmanager(scrip,stop_loss)
    Net_credit=show[4]
    Net_PL=show[0]
    CURRENT=show[1]
    stop_loss=show[2]   
    margin=show[3]
    sl_in_cash=stop_loss*(margin/100)
    strategy_profit_label.config(text=f' Net PL: {CURRENT} and Net Percentage Max Profit : {CURRENT*100/Net_credit}')
    Profit_label.config(text=f' Percentage PL:- {Net_PL} and Total Premium :- {Net_credit}')
    stop_loss_label.config(text=f' stop loss %:- {stop_loss} and SL in Cash :- {sl_in_cash}')
    margin_used.config(text=f' margin_used %: {margin}')
    last_updated_label.config(text=f'Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    root.after(5000, update_strategy_performance)
    
#def Day_mtm(script):
       # df=pd.DataFrame(api.get_positions())
        #df[['urmtom', 'rpnl']] = df[['urmtom', 'rpnl']].apply(pd.to_numeric)
        #mtm=df['urmtom'][df['tsym'].str.contains(script)].sum()
        #booked=df['rpnl'][df['tsym'].str.contains(script)].sum()
        #X=[mtm+booked,mtm,booked]
        #return  X
def calculate_strategy_profit():
    # code to calculate the profit of the trading strategy
    return 100.0

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
    mod = int(indexLtp)%100
    if mod < 50:
        atmStrike =  int(math.floor(indexLtp / 100)) * 100
    else:
        atmStrike=  int(math.ceil(indexLtp /100)) * 100
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
  

root = tk.Tk()
root.title("Algo Trade Monitor")

strategy_profit_label = tk.Label(root, text="Strategy Profit: N/A")
strategy_profit_label.pack()


stop_loss_label = tk.Label(root, text="stop loss %: N/A")
stop_loss_label.pack()

margin_used = tk.Label(root, text="margin_used : N/A")
margin_used.pack()



Profit_label = tk.Label(root, text="P & L: N/A")
Profit_label.pack()

last_updated_label = tk.Label(root, text="Last Updated: N/A")
last_updated_label.pack()

entry_button = tk.Button(root, text="Entry", command=on_entry_button_click)
entry_button.pack()

exit_button = tk.Button(root, text="Exit", command=on_exit_button_click)
exit_button.pack()

exit_button = tk.Button(root, text="Exit Screen", command=root.destroy)
exit_button.pack()

update_strategy_performance()

root.mainloop()


