# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

"""
Operations Module - Disponibiliza funções para facilitar a criação, execução e avaliação de backtests
"""

from mt5se.mt5se import date
import mt5se as se
from datetime import datetime
from datetime import timedelta
import pandas as pd 
import time
import os.path

"""
    Returns the time to the given time in the same day in seconds
"""
def secondsToTime(endHour=18, endMin=0):
    refTime=datetime.now()
    endTime=datetime.now()
    endTime=endTime.replace(hour=endHour, minute=endMin)
    d=endTime-refTime
    return d.total_seconds()

"""
    Returns the datetime expected to end today's session. For default, 17:00 (hour=17 minute=0) 
"""
def sessionEnd(hourSessionEnd=17,minSessionEnd=0):
    endTime=datetime.now()
    endTime.replace(hour=hourSessionEnd,minute=minSessionEnd)
    return endTime


"""
 Returns a specification to operations session. Parameters:
    assets,
    capital,
    endTime,
    mem,
    timeframe=se.DAILY,
    file='operation_file',
    verbose=False,
    delay=1,
    waitForOpen=False

"""
def set(assets,capital,endTime,mem,timeframe=se.DAILY,file='operation_file',verbose=False,delay=1,waitForOpen=False):
    ops=dict()  #backtest setup
    if type(waitForOpen)==bool:
        ops['waitForOpen']=waitForOpen
    else:
        print('waitForOpen should be bool')
    if type(verbose)==bool:
        ops['verbose']=verbose
    else:
        print('verbose should be bool')
        return None
    if type(delay)==float or type(delay)==int:
        ops['delay']=delay
    else:
        print('delay should be float')
        return None
    
    if type(mem)==int:
        ops['mem']=mem
    else:
        print('mem should be int')
        return None

    if type(endTime)==datetime:
        ops['end']=endTime
    else:
        print('endTime should be datetime')
        return None
    if timeframe==se.DAILY or timeframe==se.INTRADAY:
        ops['type']=timeframe
    else:
        print('type should be daily or intraday')
        return None
    if type(file)==str:
        ops['file']=file
    else:
        print('file should be str')
        return None
    if type(assets)==list:
        ops['assets']=assets
    else:
        print('assets should be list')
        return None
    if type(capital)==float or type(capital)==int:
        ops['capital']=float(capital)
    else:
        print('capital should be float')
        return None
    return ops

"""
Returns True if the given operation setup is Ok
"""
def checkOps(ops):
    try:
        if type(ops['waitForOpen'])!=bool:
            print('waitForOpen should be bool')
            return False
        if type(ops['verbose'])!=bool:
            print('verbose should be bool')
            return False
        if type( ops['mem'])!=int:
            print('mem should be int')
            return False
        if type( ops['delay'])!=int and type( ops['delay'])!=float:
            print('delay should be int or float. (seconds of delay, between to calls to trade)')
            return False
        if type(ops['start'] )!=datetime:
            print('start should be datetime')
            return False
        if type(ops['end'])!=datetime:
            print('end should be datetime')
            return False
        if ops['type']!=se.DAILY and ops['type']!=se.INTRADAY:
            print('type should be daily or intraday')
            return False
        if type(ops['file'])!=str:
            print('file should be str')
            return False
        if type(ops['assets'])!=list:
            print('assets should be list')
            return False
        if type(ops['capital'])!=float and type(ops['capital'])!=int:
            print('capital should be float')
            return False
        return True
    except:
        print("An exception occurred")
        return False



## assume-se que todos os ativos tem o mesmo numero de barras do ativo indice zero assets[0] no periodo de backtest
sim_dates=[]
balanceHist=[]
equityHist=[]
datesHist=[]
ordersHist=[]
averagePrices=dict()


"""
Returns the current time in a given operation setup
"""
def getCurrTime(ops):
    assets=ops['assets']
    bars=se.get_bars(assets[0],1,timeFrame=se.INTRADAY)
    return bars['time'][0]
    
def startOps(ops): 
    global sim_dates
    assets=ops['assets']
    dbars=dict()
    
    sim_dates.append(getCurrTime(ops))
    mem=ops['mem']
    for asset in assets:
        averagePrices[asset]=0.0
        dbar=se.get_bars(asset,mem,timeFrame=se.INTRADAY)
        if not dbar is None and not dbar.empty:
            dbars[asset]=dbar
        else:
            print("Error asset ",asset, " without information!!!")
    balanceHist.append(ops['capital'])
    equityHist.append(ops['capital'])
    datesHist.append(sim_dates[0])
    ordersHist.append(' ')
    return dbars

def getDeltaOrder(req):
    vol=req['volume']

    if se.isSellOrder(req):
        vol=-vol    
    #elif req['type']==mt5.ORDER_TYPE_BUY_LIMIT or req['type']==mt5.ORDER_TYPE_BUY:
    #    return False
    return vol

""" 
 Returns the Equity in the default currency of the stock
"""
def get_equity():
    return se.account_info().equity


def executeOrders(orders,ops,dbars):
    assets=ops['assets']
    total_in_shares=0.0
    sim_dates.append(getCurrTime(ops))
    executedOrders=[]
    txt=''
    balance=se.get_balance() 
    equity=get_equity()
    for asset in assets:
        shares=se.get_shares(asset)
        order=getOrder(orders,asset)
        # send order
        if order!=None:
            if se.checkOrder(order) and se.sendOrder(order): 
                    print('order sent to se')
                    result=se.getLastOrderResult()
                    executedOrders.append(result)
            else:
                    print('Error  : ',se.getLastError())
            txt=txt+' '+asset+', '+ str(shares)+', '+str(getDeltaOrder(order))+';'
        else:
            txt=txt+' '+asset+','+ str(shares)+', 0;'
            continue
    total_in_shares=se.get_position_value()
    if ops['verbose']==True:
        msg=str(len(orders))+' order(s) in time('+str(sim_dates[-1])+' equity={:,.2f} balance={:,.2f} '+txt
        print(msg.format(equity,balance))
    else:
        msg=str(len(orders))+' order(s) in time('+str(sim_dates[-1])+' equity={:,.2f} balance={:,.2f}. Use verbose=True for more information'
        print(msg.format(equity,balance))
    equityHist.append(equity)  # equity in operations 
    balanceHist.append(balance)
    datesHist.append(sim_dates[-1])
    prices=se.get_last_prices(assets)
    ordersHist.append(orders_to_txt(assets,orders,prices))
    return executedOrders

  
    
def orders_to_txt(assets,orders,prices):
    assets.sort()
    txt=''
    for asset in assets:
        order=getOrder(orders,asset)
        if order is not None:
            if se.isSellOrder(order):
                sinal='-'
            else:
                sinal='+'
            volume=order['volume']
        else:  # sem ordem para o ativo
            sinal=' '
            volume=0
        txt=txt+asset+'/'+sinal+str(volume)+'/'+str(prices[asset])+'/ '
    return txt

def txt_to_orders(txt):
    orders=[]
    lst=txt.split('/')
    if len(lst)%3!=1 or len(lst)<3:
        return None
    i=0
    while i<len(lst)-3:
        order=0
        symbol=lst[i].strip()
        shares=float(lst[i+1])
        price=float(lst[i+2])
        if shares>0:
            order=se.buyOrder(symbol,int(abs(shares)),price)
        elif shares<0:
            order=se.sellOrder(symbol,int(abs(shares)),price)
        else:
            order=None        
        i=i+3
        if order is not None:
            orders.append(order)
    return orders



def getOrder(orders,asset):
    for order in orders:
        if order['symbol']==asset:
            return order
    return None


def getCurrBars(ops,dbars):
    assets=ops['assets']
    #dbars=dict()
    for asset in assets:
        dbar=dbars[asset]
        #pega nova barra    
        aux=se.get_bars(asset,1,timeFrame=se.INTRADAY) # pega uma barra!
        if not aux is None and not aux.empty:
            dbar=dbar.iloc[1:,] #remove barra mais antiga
            #adiciona nova barra
            dbar=dbar.append(aux)
            dbar.index=range(len(dbar))# corrige indices
            dbars[asset]=dbar
       
    return dbars 

def getLastTime(ops):
    assets=ops['assets']
    bars=se.get_bars(assets[0],1,timeFrame=se.INTRADAY)
    return bars['time'][0]
   

def endedOps(ops):
    assets=ops['assets']
    if not se.is_market_open(assets[0]):
        print('Market is NOT open at the moment!!')
        return True
    
    if ops['verbose']:
        print('Ended?? time =',getCurrTime(ops), ' of ',len(sim_dates))
    if ops['end']==None:
        return True
    elif ops['end']<getLastTime(ops):
        return 
    else:
        return False




"""
    Start the execution of the given trader according to the operation setup given
"""
def run(trader,ops):
    se.mt5se.inbacktest=False

    if trader==None: # or type(trader)!=se.Trader:
        print("Error! Trader should be an object of class mt5se.Trader or its subclass")
        return False
    dbars=startOps(ops)
    assets=ops['assets']
    trader.setup(dbars)
    if 'delay' in ops.keys():
        delay=ops['delay']
    else:
        delay=0
    if ops['verbose']:
        print("Starting Operation at date/time=",sim_dates[0]," len=",len(sim_dates))
    if ops['waitForOpen']:
        while not se.is_market_open(assets[0]):
            print('Market is NOT open! we will wait until it is open...')
            time.sleep(1)
    while not endedOps(ops):
        orders=trader.trade(dbars)
        ex_order_list=executeOrders(orders,ops,dbars)
        trader.orders_result(ex_order_list)
        dbars=getCurrBars(ops,dbars)
        saveTick(ops)
        time.sleep(delay)
    print('End of operation saving equity file in ',ops['file'])
    trader.ending(dbars)
    df=saveEquityFile(ops)
    return df


def saveTick(ops):
    """
    print('csv format, columns: <DATE>		<BALANCE>	<EQUITY>	<DEPOSIT LOAD>')
<DATE>	            <BALANCE>	<EQUITY>	<DEPOSIT LOAD>
2019.07.01 00:00	100000.00	100000.00	0.0000
2019.07.01 12:00	99980.00	99999.00	0.0000
2019.07.01 12:59	99980.00	100002.00	0.1847
2019.07.01 12:59	99980.00	99980.00	0.0000
2019.07.02 14:59	99960.00	99960.00	0.0000
2019.07.03 13:00	99940.00	99959.00	0.0000
2019.07.03 13:59	99940.00	99940.00	0.0000
2019.07.08 15:59	99920.00	99936.00	0.0000
2019.07.08 16:59	99920.00	99978.00	0.1965
2019.07.10 10:00	99920.00	99920.00	0.0000
2019.07.10 10:59	99900.00	99937.00	0.1988
Formato gerado pelo metatrader,
ao fazer backtest com o Strategy Tester, clicar na tab 'Graphs' e botao direto 'Export to CSV (text file)'
    """
    #print('write report....')
    if len(equityHist)!=len(balanceHist) or len(balanceHist)!=len(datesHist) or len(datesHist)!=len(ordersHist):
        print("Erro!! Diferentes tamanhos de historia, de equity, balance e dates")
        print('bH=',len(balanceHist),' dH=',len(datesHist),' orderHist=',len(ordersHist))
        return False
    if len(equityHist)<=0:
        return False
    df=pd.DataFrame()
    df['date']=[]
    df['balance']=[]
    df['equity']=[]
    df['load']=[]
    df['orders']=[]
    # Salva apenas o ultimo tick
    #for i in range(len(equityHist)):
    
    i=len(equityHist)-1
    idx=len(df)
    df.loc[idx]=[datesHist[i],balanceHist[i],equityHist[i],0.0,ordersHist[i]]

    if os.path.isfile(ops['file']+'.csv'):
        df.to_csv(ops['file']+'.csv',mode='a',header=False) # file already exists, so it appends
    else:
        df.to_csv(ops['file']+'.csv')
    return df 





def saveEquityFile(ops):
    """
    print('csv format, columns: <DATE>		<BALANCE>	<EQUITY>	<DEPOSIT LOAD>')
<DATE>	            <BALANCE>	<EQUITY>	<DEPOSIT LOAD>
2019.07.01 00:00	100000.00	100000.00	0.0000
2019.07.01 12:00	99980.00	99999.00	0.0000
2019.07.01 12:59	99980.00	100002.00	0.1847
2019.07.01 12:59	99980.00	99980.00	0.0000
2019.07.02 14:59	99960.00	99960.00	0.0000
2019.07.03 13:00	99940.00	99959.00	0.0000
2019.07.03 13:59	99940.00	99940.00	0.0000
2019.07.08 15:59	99920.00	99936.00	0.0000
2019.07.08 16:59	99920.00	99978.00	0.1965
2019.07.10 10:00	99920.00	99920.00	0.0000
2019.07.10 10:59	99900.00	99937.00	0.1988
Formato gerado pelo metatrader,
ao fazer backtest com o Strategy Tester, clicar na tab 'Graphs' e botao direto 'Export to CSV (text file)'
    """
    #print('write report....')
    if len(equityHist)!=len(balanceHist) or len(balanceHist)!=len(datesHist):
        print("Erro!! Diferentes tamanhos de historia, de equity, balance e dates")
        return False
    df=pd.DataFrame()
    df['date']=[]
    df['balance']=[]
    df['equity']=[]
    df['load']=[]
    df['orders']=[]

    for i in range(len(equityHist)):
        df.loc[i]=[datesHist[i],balanceHist[i],equityHist[i],0.0,ordersHist[i]]

    if not os.path.isfile(ops['file']+'.csv'): # salva apenas se nao existir!!
       # df.to_csv(ops['file']+'.csv',mode='a',header=False) # file already exists, so it appends
        #else:
        df.to_csv(ops['file']+'.csv')
    return df 


