# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17


## chamadas que sao enviadas para a corretora (brokerage), logo exigem comunicação com a mesma 


# broker module
import MetaTrader5 as mt5
import pandas as pd 
import numpy as np 

import random
from math import *
from datetime import datetime
from datetime import timedelta
# importamos o módulo pytz para trabalhar com o fuso horário
import pytz
from pytz import timezone



sptz=pytz.timezone('Brazil/East')
etctz=pytz.timezone('etc/utc') # os tempos sao armazenados na timezone ETC (Greenwich sem horario de verao)

path=None # Metatrader program file path
datapath=None # Metatrader path to data folder
commonDatapath=None # Metatrader common data path
company=None  #broker name
platform=None  # digital plataform (M)


"""
   login,                    // número da conta  (TODO)
   password="PASSWORD",      // senha
   server="SERVER",          // nome do servidor como definido no terminal
   timeout=TIMEOUT           // tempo de espera esgotado
"""
def connect( ):
	#if not se.connect():
	#print(“Error on connection”, se.last_error())
	#exit():
    res= mt5.initialize()
    if not res:
        ac=mt5.terminal_info()
        path=ac.path
        datapath=ac.data_path
        commonDatapath=ac.commondata_path
        company=x.company
        platform=x.name
    return res


def accountInfo():
#acc=se.accountInfo()    # it returns a dictionary
#acc['login']   # Account id
#acc['balance'] # Account balance in the deposit currency
# acc['equity'] # Account equity in the deposit currency
#acc['margin']  #Account margin used in the deposit currency
#acc['margin_free'] # Free margin of an account in the deposit currency
#acc['assets'] # The current assets of an account
# acc['name'] #Client name
#  acc['server'] # Trade server name
#  acc['currency'] # Account currency, BRL for Brazilian Real 
    account_info = mt5.account_info()
    #print("account info")
    return account_info
"""
    returns the current number of assets of the given symbol
"""
def getShares(symbolId):
   pos= mt5.positions_get(symbol=symbolId)
   if pos!=None and pos!=():
      d=pos[0]._asdict() 
      return d['volume']
   else:
       return 0

   return pos['volume']


"""
  It returns if the market is open or not for new orders.
     Note that markets can close in different times for different assets, therefore
     you need to inform the target asset. The default target assets is se stock.
     It there is no tick for 60 seconds, the market is considered closed!
"""
def isMarketOpen(asset='seSA3'):
   # si=mt5.symbol_info(asset)
   # if si!=None:
  #      if si.trade_mode==mt5.SYMBOL_TRADE_MODE_FULL: # it does not work in XP/se (always True)
  #          return True
  #      else:
  #          return False
  #  return False
  t_secs=mt5.symbol_info_tick(asset).time # time in seconds
  now_dt=datetime.now(etctz)+timedelta(hours=-3)
  last_tick_dt=datetime.fromtimestamp(t_secs,etctz)
  #print(last_tick_dt)
  #print(now_dt)
  if now_dt>last_tick_dt+timedelta(seconds=60):
      return False
  else: 
      return True

"""
  It returns if the market is still open but just for closing orders.
     Note that markets can close in different times for different assets, therefore
     you need to inform the target asset. The default target assets is se stock
"""
#def isMarketClosing(asset='seSA3'): # it does not work in XP/se (always false)
#    si=mt5.symbol_info(asset)
#    if si!=None:
 #       if si.trade_mode==mt5.SYMBOL_TRADE_MODE_CLOSEONLY:
  #          return True
  #      else:
  #          return False
  #  return False


   
"""
    returns the max volume of shares thay you can buy, with your free margin
        it also observes the volume step (a.k.a minimum number of shares you can trade)
"""
def getAfforShares(assetId,money=None,price=None):
    if money==None:
        money=mt5.account_info().margin_free
    if price==None:
        close=mt5.symbol_info_tick(assetId).last
    else:
        close=price
    step=mt5.symbol_info(assetId).volume_step
    free=0
    while free*close<money:
        free=free+step
    return free-step

def getSharesStep(assetId,money=None):
    return mt5.symbol_info(assetId).volume_step
 

def sendOrder(order):
    if order==None:
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
        return True

    
def cancelOrder(o):# TO DO
   # action= TRADE_ACTION_REMOVE
    print("To do....")

def numOrders(): #returns the number of active orders
    result=mt5.orders_total()
    if result==None:
        setLastError("Error on getting orders total")
        return -1
    else:
        return result

#order fields  description:
    #order_id | buy_sell | volume | price | sl | tp | 
    #ticket | time_setup  time_setup_msc  time_expiration  type  type_time  type_filling  state  magic  
    # volume_current  price_open   sl   tp  price_current  symbol comment external_id
    #   ulong                         magic;            // Expert Advisor -conselheiro- ID (número mágico)
   #  ulong                         order;            // Bilhetagem da ordem
   #string                        symbol;           // Símbolo de negociação
  # double                        volume;           // Volume solicitado para uma encomenda em lotes
  # double                        price;            // Preço
  # double                        stoplimit;        // Nível StopLimit da ordem
  # double                        sl;               // Nível Stop Loss da ordem
  # double                        tp;               // Nível Take Profit da ordem
  # ulong                         deviation;        // Máximo desvio possível a partir do preço requisitado
 #  ENUM_ORDER_TYPE               type;             // Tipo de ordem
    #  ORDER_TYPE_BUY  Ordem de Comprar a Mercado
    #  ORDER_TYPE_SELL Ordem de Vender a Mercado
    #  ORDER_TYPE_BUY_LIMIT Ordem pendente Buy Limit
    #  ORDER_TYPE_SELL_LIMIT Ordem pendente Sell Limit
    #  ORDER_TYPE_BUY_STOP Ordem pendente Buy Stop
    #  ORDER_TYPE_SELL_STOP Ordem pendente Sell Stop
    #  ORDER_TYPE_BUY_STOP_LIMIT Ao alcançar o preço da ordem, uma ordem pendente Buy Limit é colocada no preço StopLimit
    #  ORDER_TYPE_SELL_STOP_LIMIT Ao alcançar o preço da ordem, uma ordem pendente Sell Limit é colocada no preço StopLimit
    #  ORDER_TYPE_CLOSE_BY  Ordem de fechamento da posição oposta
  # ENUM_ORDER_TYPE_FILLING       type_filling;     // Tipo de execução da ordem
    #ORDER_FILLING_FOK  Esta política de preenchimento significa que uma ordem pode ser preenchida somente na quantidade especificada. Se a quantidade desejada do ativo não está disponível no mercado, a ordem não será executada. 
  #  ENUM_ORDER_TYPE_TIME          type_time;        // Tipo de expiração da ordem
    # ORDER_TIME_DAY     Ordem válida até o final do dia corrente de negociação
  # datetime                      expiration;       // Hora de expiração da ordem (para ordens do tipo ORDER_TIME_SPECIFIED))
  # string                        comment;          // Comentário sobre a ordem
  # ulong                         position;         // Bilhete da posição
  # ulong                         position_by;      // Bilhete para uma posição oposta

def getOrders():  # returns a dataframe with all active orders
    orders=mt5.orders_get()
    if orders == None or len(orders)==0:
        print("No orders, error code={}".format(mt5.last_error()))
        return None
    else:
        print("Total orders:",len(orders))
        df=pd.DataFrame(list(orders),columns=orders[0]._asdict().keys())
        return df
      


def getDailYBars(symbol, start,end=None): # sao inclusas barras com  tempo de abertura <= end.
    # definimos o fuso horário como UTC
    #timezone = pytz.timezone("Etc/UTC")
    if end==None:
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



    return x

DAILY=mt5se.mt5se.DAILY

def get_bars(symbol, start,end=None,timeFrame=DAILY):
 # definimos o fuso horário como UTC
    #timezone = pytz.timezone("Etc/UTC")
    if symbol==None or type(symbol)!=str:
        return None
    else:
        symbol=symbol.upper()
    if timeFrame==DAILY:
        timeFrame=mt5.TIMEFRAME_D1
    elif timeFrame==INTRADAY:
        timeFrame=mt5.TIMEFRAME_M1
    else:
        timeFrame=mt5.TIMEFRAME_D1
    if end==None:
        end=datetime.now()
    if type(start).__name__!='datetime':
        if type(start).__name__!='int':
            print('Error, start should be a datetime from package datetime or int')
        else:
            start_day=datetime.now() #- timedelta(days=start)
            rates=mt5.copy_rates_from(symbol,timeFrame,start_day,start)
             # criamos a partir dos dados obtidos DataFrame
            rates_frame=pd.DataFrame(rates)
            if len(rates_frame)>0:
                rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
            return rates_frame
    else:
       rates=mt5.copy_rates_range(symbol,timeFrame,start,end)
       # criamos a partir dos dados obtidos DataFrame
       rates_frame=pd.DataFrame(rates)
       rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
       return rates_frame


def getIntradayBars(symbol, day):
    # definimos o fuso horário como UTC
    #timezone = pytz.timezone("Etc/UTC")
    if type(day).__name__!='datetime':
        print('Error, start should be a datetime from package datetime')
    else:
       rates=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,\
       day,datetime(day.year,day.month,day.day,23,59))
       # criamos a partir dos dados obtidos DataFrame
       return pd.DataFrame(rates)
##############
# datetime auxiliary functions



 