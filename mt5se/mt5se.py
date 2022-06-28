# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17


# mt5se main module
import MetaTrader5 as mt5
import pandas as pd 
import numpy as np 
import mt5se.backtest as backtest
import random
#from math import *
from datetime import datetime
from datetime import timedelta
# importamos o módulo pytz para trabalhar com o fuso horário
import pytz
from pytz import timezone



#sptz=pytz.timezone('Brazil/East')
etctz=pytz.timezone('etc/utc') # os tempos sao armazenados na timezone ETC (Greenwich sem horario de verao)

path=None # Metatrader program file path
datapath=None # Metatrader path to data folder
commonDatapath=None # Metatrader common data path
company=None  #broker name
platform=None  # digital plataform (M)
connected=False
inbacktest=False
bts=None
DAILY=mt5.TIMEFRAME_D1 # daily bars
INTRADAY=mt5.TIMEFRAME_M1 # 1 minute bars
H1=mt5.TIMEFRAME_H1 # 1 hour bars
# comprehensive list of time frames
TIMEFRAME_M1=mt5.TIMEFRAME_M1
TIMEFRAME_M2=mt5.TIMEFRAME_M2
TIMEFRAME_M3=mt5.TIMEFRAME_M3
TIMEFRAME_M4=mt5.TIMEFRAME_M4
TIMEFRAME_M5=mt5.TIMEFRAME_M5
TIMEFRAME_M6=mt5.TIMEFRAME_M6
TIMEFRAME_M10=mt5.TIMEFRAME_M10
TIMEFRAME_M12=mt5.TIMEFRAME_M12
TIMEFRAME_M15=mt5.TIMEFRAME_M15
TIMEFRAME_M20=mt5.TIMEFRAME_M20
TIMEFRAME_M30=mt5.TIMEFRAME_M30
TIMEFRAME_H1=mt5.TIMEFRAME_H1
TIMEFRAME_H2=mt5.TIMEFRAME_H2
TIMEFRAME_H3=mt5.TIMEFRAME_H3
TIMEFRAME_H4=mt5.TIMEFRAME_H4
TIMEFRAME_H6=mt5.TIMEFRAME_H6
TIMEFRAME_H8=mt5.TIMEFRAME_H8
TIMEFRAME_H12=mt5.TIMEFRAME_H12
TIMEFRAME_D1=mt5.TIMEFRAME_D1
TIMEFRAME_W1=mt5.TIMEFRAME_W1
TIMEFRAME_MN1=mt5.TIMEFRAME_MN1




def connect(account=None,passw=None,mt5path=None):
    """
   Connects to the specificied account, password and specifiec (by path) metatrader installation 
        if parameters are not specified it connects to last used account and password
"""
    if account is None and passw is None:
        if mt5path is None:
            res= mt5.initialize()
        else:
            res= mt5.initialize(mt5path)
    else:
        account=int(account)
        if mt5path is None:
            res= mt5.initialize(login=account, password=passw)
        else:
            res= mt5.initialize(mt5path,login=account, password=passw)
    global ac,path,datapath,commonDatapath,company,platform,connected
    if res!=True:
        if account is None:
            print('Error trying to connect to last account!!', ' Error code:',mt5.last_error())
        else:
            print('Error trying to connect to account: ',account, ' Error code:',mt5.last_error())
        return False
    info=mt5.account_info()
    if info.margin_so_mode !=mt5.ACCOUNT_MARGIN_MODE_RETAIL_NETTING and info.margin_so_mode !=mt5.ACCOUNT_MARGIN_MODE_EXCHANGE:
        # ACCOUNT_MARGIN_MODE_RETAIL_NETTING is usually used for simulated accounts
        # ACCOUNT_MARGIN_MODE_EXCHANGE is usually used for real accounts
        print("It is NOT netting, but the stock exchange should be netting trade mode!! Error!!")  # B3 is also Netting!!
        return False
    #elif info.margin_so_mode ==mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING:
    #    print("It is hedding, not netting")
    #else:
    #    print("It is something elese!!")
    #if info.margin_so_mode ==mt5.ACCOUNT_MARGIN_MODE_RETAIL_NETTING:
    #    print("It is netting, not hedding")  # se is Netting!!
    #elif info.margin_so_mode ==mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING:
    #    print("It is hedding, not netting")
    #else:
    #    print("It is something elese!!")
    if res:
        ac=mt5.terminal_info()
        path=ac.path
        datapath=ac.data_path
        commonDatapath=ac.commondata_path
        company=ac.company
        platform=ac.name
        connected=True
    return res

def terminal_info():
    """
    Returns info regarding the terminal in a dicitionary 
        For instance:
        'community_account': False,
        'community_connection': False,
        'connected': True, 
        'dlls_allowed': True, 
        'trade_allowed': False,
        'tradeapi_disabled': False,
        'email_enabled': False,
        'ftp_enabled': False,
        'notifications_enabled': False,
        'mqid': False,
        'build': 2875,
        'maxbars': 100000,
        'codepage': 0,
        'ping_last': 18717, 
        'community_balance': 0.0, 
        'retransmission': 0.0, 
        'company': 'MetaQuotes Software Corp.', 
        'name': 'MetaTrader 5', 
        'language': 'English', 
        'path': 'C:\\Program Files\\MetaTrader 5',
        'data_path': 'C:\\Users\\..\\AppData\\Roaming\\MetaQuotes\\Terminal\\D...', 
        'commondata_path': 'C:\\Users\\...\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common

"""
    if not connected:
        print("In order to use this function, you must be connected to the . Use function connect()")
        return
    term_info = mt5.terminal_info()
    return term_info

def account_info(): 
    """
    Returns info about the account as a dicitionary
    For instance:
  login=25115284
  trade_mode=0
  leverage=100
  limit_orders=200
  margin_so_mode=0
  trade_allowed=True
  trade_expert=True
  margin_mode=2
  currency_digits=2
  fifo_close=False
  balance=9...
  credit=0.0
  profit=41.82
  equity=9.
  margin=9..
  margin_free=9..
  margin_level=1..
  margin_so_call=50.0
  margin_so_so=30.0
  margin_initial=0.0
  margin_maintenance=0.0
  assets=0.0
  liabilities=0.0
  commission_blocked=0.0
  name=MetaQuotes Dev Demo
  server=MetaQuotes-Demo
  currency=USD
  company=MetaQuotes Software Corp.

"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    account_info = mt5.account_info()
    return account_info


def get_shares(symbolId):
    """
    Returns the current number of assets of the given symbol.
        It will be negative if there is a short position! and zero if there is no position
"""
    global inbacktest
    global bts
    if inbacktest:
        #print('Esta em backtest. bts=', bts)
        return backtest.get_shares(bts,symbolId)
    #else:
      #  print('NAO esta em backtest')
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    pos= mt5.positions_get(symbol=symbolId)
    if pos is not None and pos!=():
        d=pos[0]._asdict() 
        if d['type']==1:
            return -1*d['volume']
        else:
            return d['volume']
    else:
        return 0




def is_market_open(asset='B3SA3'):
    """
  It returns if the market is open or not for new orders.
     Note that markets can close in different times for different assets, therefore
     you need to inform the target asset. The default target assets is B3 stock (it will work only in B3 stock exchange)
     For other exchanges inform a valid asset ticker (For instance, GOOG should work for Nasdaq).
     It there is no tick for 60 seconds, the market is considered closed!
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
   # si=mt5.symbol_info(asset)
   # if siis not None:
  #      if si.trade_mode==mt5.SYMBOL_TRADE_MODE_FULL: # it does not work in XP/B3 (always True)
  #          return True
  #      else:
  #          return False
  #  return False
    mt5.symbol_select(asset) # it makes sure that the symbol is present in Market Watch View
    t_secs=mt5.symbol_info_tick(asset).time # time in seconds
    now_dt=datetime.now(etctz)+timedelta(hours=-3)
    last_tick_dt=datetime.fromtimestamp(t_secs,etctz)
    #print(last_tick_dt)
    #print(now_dt)
    if now_dt>last_tick_dt+timedelta(seconds=60):
        return False
    else: 
        return True



def today(offset=None):
    """
Returns the today datetime (hours=minutes=seconds=0)
 You can define an offset in days.
    today(1) returns tomorrow
    today(-1) returns yesterday
"""
    dt=datetime.now()
    dt=datetime(dt.year,dt.month,dt.day,0,0,0)
    if offset is None:
        return dt
    if type(offset)!=int:
        print('Offset should a int with the number of dates. Returning today date without offset')
        return dt
    else:
        dt=dt+timedelta(days=offset)
        return dt


def now(dayOffest=None,hourOffset=None,minOffset=None):
    """
    Returns the current datetime 
 You can define an offset in days,hours and minutes
    today(dayOffset=1) returns tomorrow
    today(dayOffset=-1) returns yesterday
    today(dayOffset=-1,hourOffset=-2,minOffset=-30) returns yesterday two hours and 30 minutes 
"""
    dt=datetime.now()
    if dayOffest is not None:
        dt=dt+timedelta(days=dayOffest)
    if hourOffset is not None:
        dt=dt+timedelta(hours=hourOffset)
    if minOffset is not None:
        dt=dt+timedelta(minutes=minOffset) 
    return dt

"""
  It returns if the market is still open but just for closing orders.
     Note that markets can close in different times for different assets, therefore
     you need to inform the target asset. The default target assets is B3 stock
"""
#def isMarketClosing(asset='B3SA3'): # it does not work in XP/B3 (always false)
#    si=mt5.symbol_info(asset)
#    if si is not None:
 #       if si.trade_mode==mt5.SYMBOL_TRADE_MODE_CLOSEONLY:
  #          return True
  #      else:
  #          return False
  #  return False



def get_volume_step(assetId):
    """
  Returns the volume step for an asset
"""
    step=mt5.symbol_info(assetId).volume_step
    return step
    

def get_affor_shares(assetId,price,money=None,volumeStep=None):
    """
    Returns the max volume of shares thay you can buy, with your balance
        it also observes the volume step (a.k.a minimum number of shares you can trade)
"""
    global inbacktest
    global bts
    if inbacktest:
        #print('Esta em backtest. bts=')#, bts)
        if money is None:
            money=bts['capital']
        return pget_affor_shares(assetId,price,money,volumeStep)
    #else:
      #  print('NAO esta em backtest')
    return pget_affor_shares(assetId,price,money,volumeStep)

def pget_affor_shares(assetId,price,money=None,volumeStep=None):
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    if money is None:
        money=mt5.account_info().margin_free
    if money <=0:
        return 0.0
        
    if price is None:
        close=mt5.symbol_info_tick(assetId).last
    else:
        close=price
    if volumeStep is None:
        step=get_volume_step(assetId)
    else:
        step=volumeStep    
    free=0
    while free*close<money:
        free=free+step
        #print('free=',free, ' close=',close,' money=',money  )
    return free-step


def get_balance():
    """ 
 Returns the Account balance (free resource) in the default currency of the stock
        It is equivalent to free margin in MT5 jargon
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    global inbacktest
    global bts
    if inbacktest:
        #print('Esta em backtest. bts=')#, bts)
        return backtest.get_balance(bts)
    #else:
      #  print('NAO esta em backtest')
    return mt5.account_info().margin_free





def get_position_value(symbolId=None):
    """
 Returns the current value in portfolio of a given symbol, or total value of alls symbol, if None is given
"""
    pos=get_positions(symbolId)
    if len(pos)>0:
        return sum(pos['volume']*pos['price_current'])
    else:
        return 0.0

def get_positions(symbolId=None): 
    """
 Returns a pandas dataframe with the position of a given symbol or group of symbols.
    If the parameter is None, it returns all current positions in the account
#Example:
    se.get_positions('AAPL')
  symbol  type   volume  price_open  price_current
0  EMBR3     1  47000.0       14.04          16.02

    pos['price_current']  #current price of the asset
 #print("get position")
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    if symbolId is None:
        positions=mt5.positions_get()
    else:
        positions=mt5.positions_get(symbol=symbolId)
    if len(positions)>0:
        df=pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
        df=df[['symbol','type','volume', 'price_open', 'price_current']]
        return df
    else:
        return pd.DataFrame()



def buyOrder(symbolId,volume,price=None,sl=None,tp=None): # Buying !!
    """
Creates and returns a buy order with the given symbolId, volume, price [optional], stop loss[optional], take profit [optional]
    An order is a dictionary with at least the following fields:
    "action": class of order 
    "symbol":  symbol id
    "volume": float 
    "type":  ORDER_TYPE_SELL,
    "deviation": 
    "magic": 
    "comment":
    "type_time":
    "type_filling": 
    "price":
    See also: checkOrder(ord), isSellOrder(ord), isBuyOrder(ord)
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    symbol_info = mt5.symbol_info(symbolId)
   #print("symbol=",symbolId," info=",symbol_info)
    if symbol_info is None:
        setLastError(symbolId + " not found, can not create buy order")
        return None
 
# se o símbolo não estiver disponível no MarketWatch, adicionamo-lo
    if not symbol_info.visible:
            #print(symbolId, "is not visible, trying to switch on")
            if not mt5.symbol_select(symbolId,True):
                setLastError("symbol_select({}}) failed! symbol=" +symbolId)
                return None   
    #point = mt5.symbol_info(symbolId).point
    deviation = 20
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbolId,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY,

        "deviation": deviation,
        "magic": random.randrange(100,100000),
        "comment": "order by mt5se",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    if price is None:  # order a mercado
        request['action']=mt5.TRADE_ACTION_DEAL
        request['type']=mt5.ORDER_TYPE_BUY
        request['price']=mt5.symbol_info_tick(symbolId).ask
    else:  # order limitada
        request['action']=mt5.TRADE_ACTION_PENDING
        request['type']=mt5.ORDER_TYPE_BUY_LIMIT
        request['price']=float(price)
    if sl is not None:
        request["sl"]=sl
    if tp is not None:
            request["tp"]= tp
    

    return request



def sellOrder(symbolId,volume,price=None,sl=None,tp=None): # Selling !!
    """
Creates and returns a sell order with the given symbolId, volume, price [optional], stop loss[optional], take profit [optional].
    An order is a dictionary with at least the following fields:
    "action": class of order 
    "symbol":  symbol id
    "volume": float 
    "type":  ORDER_TYPE_SELL,
    "deviation": 
    "magic": 
    "comment":
    "type_time":
    "type_filling": 
    "price":
    See also: checkOrder(ord), isSellOrder(ord), isBuyOrder(ord)
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    symbol_info = mt5.symbol_info(symbolId)
    #print("symbol=",symbolId," info=",symbol_info)
    if symbol_info is None:
        setLastError(symbolId + " not found, can not create buy order")
        return None
    # se o símbolo não estiver disponível no MarketWatch, adicionamo-lo
    if not symbol_info.visible:
        #print(symbolId, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbolId,True):
            setLastError("symbol_select({}}) failed! symbol=" +symbolId)
            return None   
    point = mt5.symbol_info(symbolId).point
    deviation = 20
    request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbolId,
    "volume": float(volume),
    "type": mt5.ORDER_TYPE_SELL,
    "deviation": deviation,
    "magic": random.randrange(100,100000),
    "comment": "order by mt5se",
    "type_time": mt5.ORDER_TIME_DAY,
    "type_filling": mt5.ORDER_FILLING_FOK,
    }
    if price is None:  # order a mercado
       request['action']=mt5.TRADE_ACTION_DEAL
       request['type']=mt5.ORDER_TYPE_SELL
       request['price']=mt5.symbol_info_tick(symbolId).ask
    else:  # order limitada
       request['action']=mt5.TRADE_ACTION_PENDING
       request['type']=mt5.ORDER_TYPE_SELL_LIMIT
       request['price']=float(price)
    if sl is not None:
       request["sl"]=sl
   
    if tp is not None:
        request["tp"]= tp
    return request


def isSellOrder(req):
    """
    Returns true if it is a sell order, False if it is a buy order.
        It sets a descriptive error message (getLastError / setLastError) if there is an error
"""
    if req is None:
        print("Error! Order is None!!!!")
        return False
    if req['type']==mt5.ORDER_TYPE_SELL_LIMIT or req['type']==mt5.ORDER_TYPE_SELL:
        return True
    elif req['type']==mt5.ORDER_TYPE_BUY_LIMIT or req['type']==mt5.ORDER_TYPE_BUY:
        return False
    else:
        print("Error! Order is not buy our sell!!!!")
        return False



def isBuyOrder(req):
    """
    Returns true if it is a sell order, False if it is a buy order.
        It sets a descriptive error message (getLastError / setLastError) if there is an error
"""
    if req is None:
        print("Error! Order is None!!!!")
        return False
    if req['type']==mt5.ORDER_TYPE_SELL_LIMIT or req['type']==mt5.ORDER_TYPE_SELL:
        return False
    elif req['type']==mt5.ORDER_TYPE_BUY_LIMIT or req['type']==mt5.ORDER_TYPE_BUY:
        return True
    else:
        print("Error! Order is not buy our sell!!!!")
        return False



def checkOrder(req):
    """
    Returns true if it a valid order
    It returns false in case of Short order or insufficient money to buy
"""
    global inbacktest
    if inbacktest:
        #print('Esta em backtest. bts=')#, bts)
        return backtest.get_balance(bts)
    #else:
      #  print('NAO esta em backtest')
    if req is None:
        return False
    result = mt5.order_check(req)
    #print('result=',result, 'req=',req)
    if result is None: # error
        setLastError(mt5.last_error())
        return False
    d=result._asdict()
    #margin - Margem requerida para a operação de negociação
    # margin_free - Margem livre que sobrará após a execução da operação de negociação
    # balance  - Valor de saldo após a execução da operação de negociação
    #for k in d.keys():
    #    print('{} = {}',k,d[k])
    if isSellOrder(req):
        if req['volume']>get_shares(req['symbol']): #bloqueia ordem a descoberto
            return False
        else:
            return True

    if d['balance']>=0 : # checa se não ficaria negativo com a execução
        return True
    else:
        setLastError('Trade would make the balance negative! Therefore, it does not check!')
        return False



lastErrorText=""

def getLastError():
    """
    Returns a string with the last error's message
"""
    global lastErrorText
    if lastErrorText is None or lastErrorText=="":
        return mt5.last_error()
    else:
        aux=lastErrorText
        lastErrorText=None  
        return aux    
 
def setLastError(error):
    """
    Sets the last error's message. Used together with getLastError
"""  
    global lastErrorText
    lastErrorText=error

lastOrderResult=""
def setLastOrderResult(order,result):
    """"
       set the result of the last order. Used together with getLastOrderResult
            result is a dictionary with four keys:
            'symbol'  - asset id
            'isSellOrder' - True if it is a sell order, false if it is a buy order
            'shares'   - Number of shares of the order
            'price'    -  Executed price for the order
    """
    global lastOrderResult
    lastOrderResult=dict()
    lastOrderResult['symbol']=order['symbol'] 
    lastOrderResult['isSellOrder']=isSellOrder(order)
    lastOrderResult['shares']=result.volume
    lastOrderResult['price']=result.price
    return lastOrderResult


def getLastOrderResult():
    """
    Returns the result of the last succesful sent order
        result is a dictionary with four keys:
            'symbol'  - asset id
            'isSellOrder' - True if it is a sell order, false if it is a buy order
            'shares'   - Number of shares of the order
            'price'    -  Executed price for the order
"""
    global lastOrderResult
    return lastOrderResult




def sendOrder(order):
    """
    Sends the given order to online execution 
        returns True if sucessfull and False otherwise
    Obs: This function should be used only for direct control traders
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    if order is None:
        return False
    # enviamos a solicitação de negociação
    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:  # if error
        print("Sent order failed < {} > retcode={}".format(result.comment,result.retcode))
        # solicitamos o resultado na forma de dicionário e exibimos elemento por elemento
        dic=result._asdict()
        setLastError(dic['comment'])
       # for field in dic.keys():
       #     print("   {}={}".format(field,dic[field]))
       #     #se esta for uma estrutura de uma solicitação de negociação, também a exibiremos elemento a elemento
       #     if field=="request":
       #         traderequest_dict=dic[field]._asdict()
       #         for tradereq_filed in traderequest_dict:
       #             print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
        return False
    else:
        setLastOrderResult(order,result)  # set the result of last sucessful order 
        return True


def numOrders(): 
    """
 Returns the number of active orders
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    result=mt5.orders_total()
    if result is None:
        setLastError("Error on getting orders total")
        return -1
    else:
        return result


def get_active_orders():  
    """
    Returns a dataframe with all active orders
order fields  description:
    #order_id | symbol | type | price | sl | tp | 
    # type: 0 - Buy (Market Order), 1  - Sell (Market Order)
            2 - Buy (LImited Order), 3 - Sell (Limited Order)
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    orders=mt5.orders_get()
    df=pd.DataFrame()
    if orders is None or len(orders)==0:
        return df
    else:
        dfaux=pd.DataFrame(list(orders),columns=orders[0]._asdict().keys())
        df['order_id']=dfaux['ticket']
        df['symbol']=dfaux['symbol']
        df['price']=dfaux['price_open']
        df['type']=dfaux['type']
        return df


def cancel_order(order_id):  
    """
    Cancels a order specified by its order_id (see get_orders).
        Returns True if the order is sucessfuly cancelled! False otherwise
            If the order does not exist, it also returns False
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    order_id=int(order_id)
    order=mt5.orders_get(ticket=order_id)
    if order is None:
        return False
    remove=dict()
    remove['action']=mt5.TRADE_ACTION_REMOVE
    remove['order']=order_id
    return mt5.order_send(remove)


def getDailYBars(symbol, start,end=None): # sao inclusas barras com  tempo de abertura <= end.
    # definimos o fuso horário como UTC
    #timezone = pytz.timezone("Etc/UTC")
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    if end is None:
        end=datetime.now()
    if type(start).__name__!='datetime':
        if type(start).__name__!='int':
            print('Error, start should be a datetime from package datetime or int')
        else:
            start_day=datetime.now() #- timedelta(days=start)
            rates=mt5.copy_rates_from(symbol,mt5.TIMEFRAME_D1,start_day,start)
             # criamos a partir dos dados obtidos DataFrame
            rates_frame=pd.DataFrame(rates)
            rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
            return rates_frame
    else:
       rates=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_D1,start,end)
       # criamos a partir dos dados obtidos DataFrame
       rates_frame=pd.DataFrame(rates)
       rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
       return rates_frame


def get_returns(bars):
    """
  Returns a serie of returns from given bars using open-close prices
    close[i]/open[i]-1
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    x=[]
    for i in range(len(bars)):
        x.append(bars['close'][i]/bars['open'][i]-1)
    return x


def get_last(bars): # argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the last close price from given bars
"""
    if bars is None:
        return 0.0
    return bars['close'].iloc[-1]


def get_first(bars):# argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the first open price from given bars
"""
    if bars is None:
        return 0
    return bars['open'][0]

def get_max(bars):# argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the max high price from given bars
"""
    if bars is None:
        return 0
    return max(bars['high'])


def get_min(bars):# argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the min low price from given bars
"""
    if bars is None:
        return 0
    return max(bars['low'])


def get_last_time(bars): # argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the last time from given bars
"""
    if bars is None:
        return 0
    return bars['time'].iloc[-1]

def get_first_time(bars):# argumento deve ser bars nao vazia, retorna erro se estiver vazia
    """
  Returns the first (earlier) time from given bars
"""
    if bars is None:
        return 0
    return bars['time'][0]


def read_bars_file(fileName):
    """
 Returns a pandas data frame with the content of the bars file given as parameter.
    Bars files are csv files that can be obtained from MetaTrader with the following nine columns:
     date,time,open,high,low,close,vol, tickvol,spread
"""
    df=pd.read_csv(fileName,delimiter='\t',names=['date','time','open','high','low','close','vol', 'tickvol','spread'],header=0) 
    if df is None or len(df.columns)!=9:
        print("The bars file should be a csv file with nine columns: date,time,open,high,low,close,vol, tickvol,spread")
        return None
    else:
        return df

def get_bars(symbol, start,end=None,timeFrame=DAILY):
    """
 Returns a pandas data frame with bars information. Parameters
    symbol - the asset symbol
    start - the start date or the number of the last x desired bars
    end - the end date [optional] 
    timeFrame - the bars time frame, it may be DAILY (default) (1 day bars) or INTRADAY (1 minute bars)
        There are others possible time frames, for 1 minute (TIMEFRAME_M1), 2 minutes, 1 hour (TIMEFRAME_H1), two hours, 1 week(TIMEFRAME_W1), one month(TIMEFRAME_MN1), etc.
            TIMEFRAME_M1
            TIMEFRAME_M2
            TIMEFRAME_M3
            TIMEFRAME_M4
            TIMEFRAME_M5
            TIMEFRAME_M6
            TIMEFRAME_M10
            TIMEFRAME_M12
            TIMEFRAME_M15
            TIMEFRAME_M20
            TIMEFRAME_M30
            TIMEFRAME_H1
            TIMEFRAME_H2
            TIMEFRAME_H3
            TIMEFRAME_H4
            TIMEFRAME_H6
            TIMEFRAME_H8
            TIMEFRAME_H12
            TIMEFRAME_D1
            TIMEFRAME_W1
            TIMEFRAME_MN1
    For instance,
        se.get_bars('AAPL',10) # returns the last 10 daily bars    
        time   open   high    low  close  tick_volume  spread  real_volume
"""
 # definimos o fuso horário como UTC
    #timezone = pytz.timezone("Etc/UTC")
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    if symbol is None or type(symbol)!=str:
        return None
    else:
        symbol=symbol.upper()
    if timeFrame in [DAILY,H1,INTRADAY,TIMEFRAME_M1,TIMEFRAME_M2,TIMEFRAME_M3,TIMEFRAME_M4	,TIMEFRAME_M5,TIMEFRAME_M6,TIMEFRAME_M10,TIMEFRAME_M12,TIMEFRAME_M15,  \
    TIMEFRAME_M20,TIMEFRAME_M30,TIMEFRAME_H1,TIMEFRAME_H2,TIMEFRAME_H3,TIMEFRAME_H4,TIMEFRAME_H6,TIMEFRAME_H8,TIMEFRAME_H12,TIMEFRAME_D1,TIMEFRAME_W1,TIMEFRAME_MN1]:
        # if it is a valid time frame it just continues
        pass
    else:  # if timeframe is invalid, assumes it is daily
        timeFrame=mt5.TIMEFRAME_D1
    if end is None:
        #if timeFrame!=mt5.TIMEFRAME_M1:
        end=datetime.now()
        #else: # intraday, end=None then end is the same as start
        #    end=start
    if type(start).__name__!='datetime' and type(start).__name__!='Timestamp':
        if type(start).__name__!='int':
            print('Error, start should be a datetime or int, but it is ',type(start).__name__)
            return None
        else:
            start_day=datetime.now() #- timedelta(days=start)
            rates=mt5.copy_rates_from(symbol,timeFrame,start_day,start)
             # criamos a partir dos dados obtidos DataFrame
            rates_frame=pd.DataFrame(rates)
            if len(rates_frame)>0:
                rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
            return rates_frame
    else:
        if type(end).__name__=='int':
            rates=mt5.copy_rates_from(symbol,timeFrame,start,end)
        else:
            rates=mt5.copy_rates_range(symbol,timeFrame,start,end)
       # criamos a partir dos dados obtidos DataFrame
        rates_frame=pd.DataFrame(rates)
        if len(rates_frame)>0:
            rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        return rates_frame




def get_multi_bars(assets,start,end=None,type=DAILY):
    """
Returns bars for multiple assets. It is similar to get_bars (that deals with just one asset)
    mbars=get_multi_bars(assets,start,end)
    mbars[assets[0]] # bars for the first asset (0)
"""
    dbars=dict()
    for asset in assets:
        dbars[asset]=get_bars(asset,start,end,type)
    return dbars




def get_orders(start,end,allFields=False):
    """
Returns list of orders for a given period of time  (start-end)as pandas DataFrame
    Parameters: start,end (datetime from datetime)
                allFields=False (by default only the main fields are returned)
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    lis2=mt5.history_orders_get(start,end)
    df2=pd.DataFrame(list(lis2),columns=lis2[0]._asdict().keys())
    if not allFields:
        df2.drop(['time_setup_msc','time_done_msc','time_setup_msc','time_expiration','type_time','state','position_by_id','reason','volume_current','price_stoplimit','sl','tp'], axis=1, inplace=True)
    df2['time_setup'] = pd.to_datetime(df2['time_setup'], unit='s')
    df2['time_done'] = pd.to_datetime(df2['time_done'], unit='s')
    #df2['type'] =df2['type'].map(type_order)
    #df2['reason'] =df2['reason'].map(reason)
    return df2



def get_deals(start,end,allFields=False):
    """
Returns list of deals for a given period of time  (start-end)as pandas DataFrame
    deals - include executed orders and orders executed by the broker (margin calls, withdraws, deposits and others)
    Parameters: start,end (datetime from datetime)
                allFields=False (by default only the main fields are returned)
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    lis2=mt5.history_deals_get(start,end)
    df2=pd.DataFrame(list(lis2),columns=lis2[0]._asdict().keys())
    if not allFields:
        df2.drop(['entry','swap','external_id','time_msc','magic','order','position_id'], axis=1, inplace=True) 
    df2['time']=pd.to_datetime(df2['time'], unit='s')
    #df2['type'] =df2['type'].map(type_order)
    #df2['reason'] =df2['reason'].map(reason)
    return df2




# Funcoes auxiliares para type and reason of order and deals
def order_type(x):
    """ 
        Returns a string with type of order 
        0 - ORDER_TYPE_BUY - Market Buy order
        1 - ORDER_TYPE_SELL - Market Buy order
        2 - ORDER_TYPE_BUY_LIMIT - Buy Limit pending order
        3 - ORDER_TYPE_SELL_LIMIT - Sell Limit pending order
        4 - ORDER_TYPE_BUY_STOP - Buy Stop pending order
        5 - ORDER_TYPE_SELL_STOP - Sell Stop pending order
        6 - ORDER_TYPE_BUY_STOP_LIMIT - Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
        7 - ORDER_TYPE_SELL_STOP_LIMIT - AUpon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
        8 - ORDER_TYPE_CLOSE_BY - Order to close a position by an opposite one
    """
    if x==0:
        #Market Buy order
        return 'BUY'
    elif x==1:
        #Market Sell order
        return 'SELL'
    elif x==2: 
        #Buy Limit pending order
        return 'LIMTED_BUY'
    elif x==3:
        #Sell Limit pending order
        return 'LIMITED_SELL'
    elif x==4:
        #Buy Stop pending order
        return 'ORDER_TYPE_BUY_STOP'
    elif x==5:
        #Sell Stop pending order
        return 'ORDER_TYPE_SELL_STOP'
    elif x==6:
        #Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
        return 'ORDER_TYPE_BUY_STOP_LIMIT'
    elif x==7:
        #Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
        return 'ORDER_TYPE_SELL_STOP_LIMIT'
    elif x==8:
        #Order to close a position by an opposite one
        return 'ORDER_TYPE_CLOSE_BY'
    else:
        return 'UNKNOWN'


def order_reason(x):
    """
        Returns a string with the reason of a given order. Possible values:
        0 - ORDER_REASON_CLIENT - The order was placed from a desktop terminal
        1 - ORDER_REASON_MOBILE - The order was placed from a mobile application
        2 - ORDER_REASON_WEB - The order was placed from a web platform
        3 - ORDER_REASON_EXPERT - The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
        4 - ORDER_REASON_SL - The order was placed as a result of Stop Loss activation
        5 - ORDER_REASON_TP - The order was placed as a result of Take Profit activation
        6 - ORDER_REASON_SO - The order was placed as a result of the Stop Out event
    """
    if x==0:
        # Ordem colocada a partir de um terminal desktop
        return 'ORDER_REASON_CLIENT'
    elif x==1:
        #Ordem colocada a partir de um aplicativo móvel
        return 'ORDER_REASON_MOBILE'
    elif x==2:
        #Ordem colocada a partir da plataforma web
        return 'ORDER_REASON_WEB'
    elif x== 3:
        #Ordem colocada a partir de um programa MQL5, Expert Advisor ou script
        return 'ORDER_REASON_EXPERT'
    elif x== 4:
        #Ordem colocada como resultado da ativação do Stop Loss
        return 'ORDER_REASON_SL'
    elif x== 5:
        #Ordem colocada como resultado da ativação do Take Profit
        return 'ORDER_REASON_TP'
    elif x== 6:
        #Ordem colocada como resultado do evento Stop Out
        return 'ORDER_REASON_SO'
    else:
        return 'UNKNOWN'



def deal_type(x):
    """
        Returns a string with type of a deal. Possible values:
        0 - DEAL_TYPE_BUY - Buy
        1 - DEAL_TYPE_SELL - Sell
        2 - DEAL_TYPE_BALANCE - Balance
        3 - DEAL_TYPE_CREDIT - Credit
        4 - DEAL_TYPE_CHARGE -Additional charge
        5 - DEAL_TYPE_CORRECTION - Correction
        6 - DEAL_TYPE_BONUS - Bonus
        7 - DEAL_TYPE_COMMISSION - Additional commission
        8 - DEAL_TYPE_COMMISSION_DAILY - Daily commission
        9 - DEAL_TYPE_COMMISSION_MONTHLY - Monthly commission
        10 - DEAL_TYPE_COMMISSION_AGENT_DAILY - Daily agent commission
        11 - DEAL_TYPE_COMMISSION_AGENT_MONTHLY - Monthly agent commission
        12 - DEAL_TYPE_INTEREST - Interest rate
        13 - DEAL_TYPE_BUY_CANCELED - Canceled buy deal. There can be a situation when a previously executed buy deal is canceled. In this case, the type of the previously executed deal (DEAL_TYPE_BUY) is changed to DEAL_TYPE_BUY_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated balance operation
        14 - DEAL_TYPE_SELL_CANCELED - Canceled sell deal. There can be a situation when a previously executed sell deal is canceled. In this case, the type of the previously executed deal (DEAL_TYPE_SELL) is changed to DEAL_TYPE_SELL_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated balance operation
        15 - DEAL_DIVIDEND - Dividend operations
        16 - DEAL_DIVIDEND_FRANKED - Franked (non-taxable) dividend operations
        17 - DEAL_TAX - Tax charges
    """
    if x==0:
        # Compra
        return 'DEAL_TYPE_BUY'
    elif x==1:
        # Venda
        return 'DEAL_TYPE_SELL'
    elif x== 2:
        # Saldo
        return 'DEAL_TYPE_BALANCE'
    elif x== 3:
        # Crédito
        return 'DEAL_TYPE_CREDIT'
    elif x== 4:
        # Cobrança adicional
        return 'DEAL_TYPE_CHARGE'
    elif x==5 :
        # Correção
        return 'DEAL_TYPE_CORRECTION'
    elif x== 6:
        # Bonus
        return 'DEAL_TYPE_BONUS'
    elif x==7:
        # Comissão adicional
        return 'DEAL_TYPE_COMMISSION'
    elif x== 8:
        # Comissão diária
        return 'DEAL_TYPE_COMMISSION_DAILY'
    elif x== 9:
        # Comissão mensal
        return 'DEAL_TYPE_COMMISSION_MONTHLY'
    elif x== 10:
        # Comissão de agente diário
        return 'DEAL_TYPE_COMMISSION_AGENT_DAILY'
    elif x== 11:
        # Comissão de agente mensal
        return 'DEAL_TYPE_COMMISSION_AGENT_MONTHLY'
    elif x== 12:
        # Taxa de juros
        return 'DEAL_TYPE_INTEREST'
    elif x== 13:
        # Operação de compra cancelada. Pode haver uma situação quando uma operação de compra executada anteriormente é cancelada. Neste caso, o tipo de transação executada anteriormente (DEAL_TYPE_BUY) é alterada para DEAL_TYPE_BUY_CANCELED, e seu lucro/prejuízo é zerado Lucro/prejuízo obtido anteriormente é cobrado/sacado usando uma operação de saldo separada
        return 'DEAL_TYPE_BUY_CANCELED'
    elif x==14 :
        # Operação de venda cancelada. Pode haver uma situação quando uma operação de venda executada anteriormente é cancelada. Neste caso, o tipo da operação executada anteriormente (DEAL_TYPE_SELL) é alterada para DEAL_TYPE_SELL_CANCELED, e seu lucro/prejuízo é zerado. Lucro/prejuízo obtido anteriormente é cobrado/sacado usando uma operação de saldo separada
        return 'DEAL_TYPE_SELL_CANCELED'
    elif x==15 :
        # Operação de dividendos
        return 'DEAL_DIVIDEND'
    elif x== 16:
        # Operação de dividendos franqueados (não tributáveis)
        return 'DEAL_DIVIDEND_FRANKED'
    elif x== 17:
        # Cálculo do imposto
        return 'DEAL_TAX'
    else:
        return 'UNKNOWN'


def deal_reason(x):
    """
        Returns a string with the reason of a deal. Possible values:
        0 - DEAL_REASON_CLIENT - The deal was executed as a result of activation of an order placed from a desktop terminal
        1 - DEAL_REASON_MOBILE - The deal was executed as a result of activation of an order placed from a mobile application
        2 - DEAL_REASON_WEB - The deal was executed as a result of activation of an order placed from the web platform
        3 - DEAL_REASON_EXPERT - The deal was executed as a result of activation of an order placed from an MQL5 program or mt5se,  i.e. an Expert Advisor or a script
        4 - DEAL_REASON_SL  - The deal was executed as a result of Stop Loss activation
        5 - DEAL_REASON_TP - The deal was executed as a result of Take Profit activation
        6 - DEAL_REASON_SO - The deal was executed as a result of the Stop Out event
        7 - DEAL_REASON_ROLLOVER - The deal was executed due to a rollover
        8 - DEAL_REASON_VMARGIN - The deal was executed after charging the variation margin
        9 - DEAL_REASON_SPLIT - The deal was executed after the split (price reduction) of an instrument, which had an open position during split announcement
    """
    if x==0:
        #Transação realizada como resultado da ativação de uma ordem colocada a partir de um terminal desktop
        return 'DEAL_REASON_CLIENT'
    elif x==1:
        #Transação realizada como resultado da ativação de uma ordem colocada a partir de um aplicativo móvel
        return 'DEAL_REASON_MOBILE'
    elif x==2:
        #Transação realizada como resultado da ativação de uma ordem colocada a partir da plataforma web
        return 'DEAL_REASON_WEB'
    elif x== 3:
        #Transação realizada como resultado da ativação de uma ordem colocada a partir de um programa MQL5, Expert Advisor ou script
        return 'DEAL_REASON_EXPERT'
    elif x== 4:
        #Transação realizada como resultado da ativação de uma ordem Stop Loss
        return 'DEAL_REASON_SL'
    elif x== 5:
        #Transação realizada como resultado da ativação de uma ordem Take Profit
        return 'DEAL_REASON_TP'
    elif x== 6:
        #Transação realizada como resultado do evento Stop Out
        return 'DEAL_REASON_SO'
    elif x== 7:
        #Transação realizada devido à transferência da posição
        return 'DEAL_REASON_ROLLOVER'
    elif x== 8:
        #Transação realizada após creditada/debitada a margem de variação
        return 'DEAL_REASON_VMARGIN'
    elif x== 9:
        #Transação realizada após o fracionamento (redução do preço) do instrumento que tinha a posição aberta durante o fracionamento    
        return 'DEAL_REASON_SPLIT'
    else:
        return 'UNKNOWN'




"""
Returns intraday (1 minute) bars.
     It is the same as se.get_bars(symbol,day,timeFrame=se.INTRADAY)
    see get_bars()
def get_intraday_bars(symbol, day):
    return get_bars(symbol,day,timeFrame=INTRADAY)
"""

"""
"""

def roll_bars(bars, new_bars):
    len_new=len(new_bars)
    if len(bars)<=len_new:
        print('The length of bars',len(bars),' should be bigger than the lenght of new_bars ',len(new_bars))
        return bars
    for i in range(len_new):
        bars=bars.drop(i)
    bars=bars.append(new_bars)
    bars=bars.reset_index()
    del bars['index']
    return bars




def get_close_prices(assets,start,end=None,timeFrame=DAILY):
    """
 Returns a pandas.DataFrame like the one below for a group of assets. It is similar to get_multi_bars.
                XOM        RRC        BBY         MA        PFE        JPM
date
2010-01-04  54.068794  51.300568  32.524055  22.062426  13.940202  35.175220
2010-01-05  54.279907  51.993038  33.349487  21.997149  13.741367  35.856571
2010-01-06  54.749043  51.690697  33.090542  22.081820  13.697187  36.053574
..
# Note that 'date' column is the index, the others are assets' close prices
"""
    if not connected:
        print("In order to use this function, you must be connected to the Stock Exchange. Use function connect()")
        return
    df=pd.DataFrame()
    first=True
    for asset in assets:
        bars=get_bars(asset,start,end,timeFrame)
        if first:
            df['date']=bars['time']
            first=False
        df[asset]=bars['close']
    df=df.set_index('date')
    return df

def get_close_prices_from_dbars(assets,dbars):
    """
Returns a pd.DataFrame like the one below for a group of assets from given multi asset bars
    It is similar to get_multi_bars.
                XOM        RRC        BBY         MA        PFE        JPM
date
2010-01-04  54.068794  51.300568  32.524055  22.062426  13.940202  35.175220
2010-01-05  54.279907  51.993038  33.349487  21.997149  13.741367  35.856571
2010-01-06  54.749043  51.690697  33.090542  22.081820  13.697187  36.053574
2010-01-07  54.577045  51.593170  33.616547  21.937523  13.645634  36.767757
2010-01-08  54.358093  52.597733  32.297466  21.945297  13.756095  36.677460
 Note that 'date' column is the index, the others are assets' close prices
"""
    df=pd.DataFrame()
    first=True
    for asset in assets:
        bars=dbars[asset]
        if first:
            df['date']=bars['time']
            first=False
        df[asset]=bars['close']
    df=df.set_index('date')
    return df


def mean_historical_return(df,geometric=True):
    """
    Returns the historical mean, it can be geometric (default) or arithmetic
    If the data is daily, the mean is daily.
"""
    expected_returns=dict()
    assets=df.keys()
    for asset in assets:
        size=len(df[asset])
        ret=0
        if not geometric: #arithmetic
            for i in range(size-1):
                ret=ret+(df[asset][i+1]/df[asset][i]-1)
            expected_returns[asset]=ret/(size-1)
        else:
            ret=(df[asset][size-1]/df[asset][0])
            expected_returns[asset]=ret**(1/(size-1))-1         
    return expected_returns



def get_last_prices(assets,dbars=None):
    """
    Returns a dictionary with the last prices of set of assets
        the symbol tickets are the dictionary keys
"""
    last_prices=dict()
    if dbars is not None:
        for asset in assets:
            last_prices[asset]=get_last(dbars[asset])
    else:
        for asset in assets:
            bars=get_bars(asset,1,timeFrame=INTRADAY)
            last_prices[asset]=get_last(bars)
    return last_prices


def get_volume_steps(assets):
    """
    Returns a dictionary with the volume steps of set of assets
"""
    steps=dict()
    for asset in assets:
        steps[asset]=get_volume_step(asset)
    return steps


def get_curr_shares(assets=None):
    """
    Returns a dictionary with the current number of shares for a list of assets.
    If no list is provided (None), it returns a dictionary for all assets with non zero position
"""
    if assets is None:
        cshares=dict()
        pos=mt5.positions_get()
        for p in pos:
            cshares[p.symbol]=p.volume
        return cshares
    cshares=dict()
    for asset in assets:
        cshares[asset]=get_shares(asset)
    return cshares


def orders_from_weights(weights,last_prices,capital):
    """
    Returns a list of orders to adopt a portfolio defined by a set of weights (dictionary),
        a set of last prices (dictionary) and the amount of available capital 
"""
    # sort weights from highest to lowest
    weights=dict(sorted(weights.items(), key=lambda item:item[1],reverse=True))
    #round 1 - buy while never exceeds the desired weight
    assets=weights.keys()
    sum=0
    curr=dict() # current weights
    volumes=dict() #  order's volumes
    steps=get_volume_steps(assets)
    for asset in assets:
        aval_capital=weights[asset]*capital
        shares=get_affor_shares(asset,last_prices[asset],aval_capital,steps[asset])
        if shares<=0:
            curr[asset]=0
            volumes[asset]=0
        else:
            curr[asset]=(shares*last_prices[asset])/capital
            volumes[asset]=shares
        sum=sum+curr[asset]
    #round 2 - if there is remainig capital, buy more lot according weight order 
    remain_capital=capital-sum*capital
    if remain_capital<=0:
        return volumes
    for asset in weights.keys():
        s=steps[asset]
        p=last_prices[asset]
        missing=(weights[asset]-curr[asset])*capital
        while s*p<remain_capital and s*p<missing:
            s=s+steps[asset]
        if s*p>remain_capital :
            s=s-steps[asset]
        curr[asset]=curr[asset]+(s*p)/capital
        volumes[asset]=volumes[asset]+s
        remain_capital=remain_capital-s*p
        if remain_capital<=0:
            break
    return volumes


def get_new_orders_from_curr_shares(orders,curr_shares):
    """
    Get new adjusted orders considering current shares of a set of assets, and orders to buy a certain
    numbers of shares for each asset. For instance,
        if orders define buy 1000 of X and 500 of Y and currently the account has 100 shares of X and 900 shares of Y
        the new orders would be buy 900 shares of X and sell 400 shares of Y.
"""
    new_orders=dict()
    for k in orders.keys():
        new_orders[k]=orders[k]-curr_shares[k]
    return new_orders




def date(year,month,day,hour=0,min=0,sec=0):
    """
    Returns a datetime with the specified year,month,day,hour=0,min=0,sec=0
"""
    return datetime(year,month,day,hour,min,sec)


###############################
# Classes used in inverse control trader and backtest!!
class Trader:
    """
        Basic Trader class for mt5se
    """
    def __init__(self):
        """
            Trader's constructor
        """
        pass
    # Receives dbars[asset] - a bars dataframe for each asset in a dictionary
    #   and setups the operation
    def setup(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
       and prepares the trader for execution. It is called once, just after trader creation
        """
        pass

    def trade(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
       and returns a list of orders with up to one order for each asset. It is called every trading cycle
        """
        pass

    def orders_result(self, exec_orders):
        """
            Receive a list of executed orders. It is called after Trader.trade() with the list of orders given by Trader.trader that were really executed.
            Receives orders_res_list - a list of the orders really executed with real volume and price
       Each result is a dictionary 'order' with:
        order['symbol'] - string
        order['isSellOrder'] - boolean
        order['shares'] - float
        order['price'] - float
        It is called once at every trading cycle
     """
        pass

    def ending(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
        It is called once, just before trader's end of execution
        """
        pass
 

class Analyst:
    """
        Basic Analyst class for mt5se. It may be used for Trader to get target prices.
    """
    def __init__(self):
        """
            Analyst's constructor
        """
        pass
    # Receives dbars[asset] - a bars dataframe for each asset in a dictionary
    #   and setups the operation
    def setup(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
       and prepares the analyst for execution. It is called once, just after trader creation
        """
        pass

    def analyze(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
       and returns a list of target price for each asset (-1 if not available for a given asset). It is called every trading cycle
        """
        pass
   
    def ending(self,dbars):
        """
            Receives dbars[asset] - a bars dataframe for each asset in a dictionary
        It is called once, just before analyst's end of execution
        """
        pass