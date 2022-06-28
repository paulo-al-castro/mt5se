# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17


"""
Backtest Module - Disponibiliza funções para facilitar a criação, execução e avaliação de backtests
"""

import mt5se as se
from datetime import datetime
from datetime import timedelta
import pandas as pd 
import numpy as np
import os.path


def set(assets,prestart,start,end,period,capital,file='backtest_file',verbose=False):

    bts=dict()  #backtest setup
    if type(verbose)==bool:
        bts['verbose']=verbose
    else:
        print('verbose should be bool')
        return None
    if type(prestart)==datetime:
        bts['prestart']=prestart
    else:
        print('prestart should be datetime')
        return None
    if type(start)==datetime:
        bts['start']=start
    else:
        print('start should be datetime')
        return None
    if type(end)==datetime:
        bts['end']=end
    else:
        print('end should be datetime')
        return None
    if period==se.DAILY or period==se.INTRADAY or period==se.H1:
        bts['type']=period
    else:
        print('type should be daily or intraday or H1')
        return None
    if type(file)==str:
        bts['file']=file
    else:
        print('file should be str')
        return None
    if type(assets)==list:
        bts['assets']=assets
    else:
        print('assets should be list')
        return None
    if type(capital)==float or type(capital)==int:
        bts['capital']=float(capital)
    else:
        print('capital should be float')
        return None
    return bts

def get_shares(bts,asset):
    return bts['shares_'+asset]

def get_balance(bts):
    return bts['capital']



## assume-se que todos os ativos tem o mesmo numero de barras do ativo indice zero assets[0] no periodo de backtest
sim_dates=[]

def startBckt(bts): 
    global sim_dates
    assets=bts['assets']
    dbars=dict()
    for asset in assets:
        dbars[asset]=se.get_bars(asset,bts['prestart'],bts['start'],bts['type'])
        bts['shares_'+asset]=0.0
    bars=se.get_bars(assets[0],bts['start'],bts['end'],bts['type'])
    
    sim_dates=bars['time']
   
    bts['curr']=0 # guarda a data simulada corrente como indice de sim_dates
    
    #balanceHist.append(bts['capital'])
    #equityHist.append(bts['capital'])
    #datesHist.append(sim_dates[bts['curr']])
    return dbars

def endedBckt(bts):
    if bts['verbose']:
        print('Ended?? time =', bts['curr'], ' of ',len(sim_dates))
    if bts['curr']==None or bts['end']==None:
        return True
    elif bts['curr']<len(sim_dates):
        return False
    else:
        return True


balanceHist=[]
equityHist=[]
datesHist=[]
ordersHist=[]

def checkOrder(req,bts,bars):
    if req==None:
        return False
    money=bts['capital']
    asset=req['symbol']
    volume=req['volume']
    price=se.get_last(bars)
    sell=se.isSellOrder(req)

    if sell:
        if bts['shares_'+asset]>=volume:
            return True
        else:
            return False
    else:
        if money>=volume*price : # checa se não ficaria negativo com a execução
            return True
        else:
            se.setLastError('Trade would make the balance negative! Therefore, it does not check!')
        return False


def compute_order(order,volume,price):
    lastOrderResult=dict()
    lastOrderResult['symbol']=order['symbol'] 
    lastOrderResult['isSellOrder']=se.isSellOrder(order)
    lastOrderResult['shares']=volume
    lastOrderResult['price']=price
    return lastOrderResult





def computeOrders(orders,bts,dbars):
    assets=bts['assets']
    total_in_shares=0.0
    executedOrdersList=[]
    if orders==None:
        equityHist.append(equityHist[-1])
        balanceHist.append(balanceHist[-1])
        datesHist.append(sim_dates[bts['curr']])
        for asset in assets:
            bar=dbars[asset]
            price=se.get_last(bar)
            total_in_shares=total_in_shares+bts['shares_'+asset]*price # counts the value in asset with no order
        if bts['verbose']:
            print( 'No orders in time(',bts['curr'],') = ',sim_dates[bts['curr']],' capital=',bts['capital'], 'total in shares=',total_in_shares)
        return True
    
    if bts['verbose']:
        print('List of ',len(orders),'orders in time(',bts['curr'],') :')
    for asset in assets:
        bar=dbars[asset]
        if bar is None:
            print('Error accesing bar to compute order')
            return False
        price=se.get_last(bar)
        order=getOrder(orders,asset)
        if order==None: # if no order for that asset, go to the next
            total_in_shares=total_in_shares+bts['shares_'+asset]*price # counts the value in asset with no order
            continue
        volume=order['volume']
        if se.isSellOrder(order):
            bts['shares_'+asset]=bts['shares_'+asset]-volume
            bts['capital']=bts['capital']+volume*price
            if bts['verbose']:
                print("Order for selling ",volume,"shares of asset=",asset, " at price=",price)
        else:
            bts['shares_'+asset]=bts['shares_'+asset]+volume
            bts['capital']=bts['capital']-volume*price
            if bts['verbose']:
                print("Order for buying ",volume,"shares of asset=",asset, " at price=",price)
        ord_result=compute_order(order,volume,price)
        executedOrdersList.append(ord_result)
        total_in_shares=total_in_shares+float(bts['shares_'+asset])*price # counts the value in asset with order
    if bts['verbose']:
        print( len(orders),' order(s) in time(',bts['curr'],') = ',sim_dates[bts['curr']],' capital=',bts['capital'], 'total in shares=',total_in_shares, 'equity=',bts['capital']+total_in_shares)
    equityHist.append(bts['capital']+total_in_shares)
    balanceHist.append(bts['capital'])
    datesHist.append(sim_dates[bts['curr']])
    #detalhamento das ordens
    prices=se.get_last_prices(assets)
    ordersHist.append(se.operations.orders_to_txt(assets,orders,prices))
    return executedOrdersList
    

def getOrder(orders,asset):
    for order in orders:
        if order['symbol']==asset:
            return order
    return None


def getCurrBars(bts,dbars):
    assets=bts['assets']
    #dbars=dict()
    for asset in assets:
        dbar=dbars[asset]
        #pega nova barra    
        aux=se.get_bars(asset,sim_dates[bts['curr']],1,bts['type']) # pega uma barra! daily or intraday
        if not aux is None and not aux.empty:
            dbar=dbar.iloc[1:,] #remove barra mais antiga
            #adiciona nova barra
            dbar=dbar.append(aux)
            dbar.index=range(len(dbar))# corrige indices
            dbars[asset]=dbar
       
    return dbars 

def checkBTS(bts):
    try:
        if type(bts['verbose'])!=bool:
            print('verbose should be bool')
            return False
        if type( bts['prestart'])!=datetime:
            print('prestart should be datetime')
            return False
        if type(bts['start'] )!=datetime:
            print('start should be datetime')
            return False
        if type(bts['end'])!=datetime:
            print('end should be datetime')
            return False
        if bts['type']!=se.DAILY and bts['type']!=se.INTRADAY and bts['type']!=se.H1:
            print('type should be daily or intraday or H1')
            return False
        if type(bts['file'])!=str:
            print('file should be str')
            return False
        if type(bts['assets'])!=list:
            print('assets should be list')
            return False
        if type(bts['capital'])!=float and type(bts['capital'])!=int:
            print('capital should be float')
            return False
        return True
    except:
        print("An exception occurred")
        return False

def run(trader,bts):
    se.mt5se.inbacktest=True
    se.mt5se.bts=bts
    balanceHist.clear()
    equityHist.clear()
    datesHist.clear()
    if trader==None: # or type(trader)!=se.Trader:
        print("Error! Trader should be an object of class mt5se.Trader or its subclass")
        return False
    if not checkBTS(bts):
        print("The Backtest setup (bts) is not valid!")
        return False
    dbars=startBckt(bts)
    trader.setup(dbars)
    bts['curr']=0
    if bts['verbose']:
        print("Starting at simulated date=",sim_dates[0]," len=",len(sim_dates))
    while not endedBckt(bts):
        #orders=trader.getNewInfo(dbars)
        orders=trader.trade(dbars)
        dbars=getCurrBars(bts,dbars)
        ex_orders_list=computeOrders(orders,bts,dbars)
        trader.orders_result(ex_orders_list)
        if bts['verbose']:
            print("Advancing simulated date from ",bts['curr']," = ",sim_dates[bts['curr']])
        bts['curr']=bts['curr']+1 # advances simulated time
    print('End of backtest with ',bts['curr'],' bars,  saving equity file in ',bts['file'])
    trader.ending(dbars)
    df=saveEquityFile(bts)
    se.mt5se.inbacktest=False
    return df


def saveEquityFile(bts):
    """
    print('csv format, columns: <DATE>		<BALANCE>	<EQUITY>	<DEPOSIT LOAD>')
<DATE>	            <BALANCE>	<EQUITY>	<DEPOSIT LOAD> <orders>
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

    if os.path.isfile(bts['file']+'.csv'):
        df.to_csv(bts['file']+'.csv',mode='a',header=False) # file already exists, so it appends
    else:
        df.to_csv(bts['file']+'.csv') 
    return df 


def evaluate(df):
   #rreturns=__calcReturns(df['equity'])
   """ print('---rreturns------')
   print(rreturns)
   for r in rreturns:
       print(r)
   print('---rreturns------') """
   #if df==None:
   #    print('Error!! df should be a DataFrame with a equity column')
   evaluateEquitySerie(df['equity'])



#using Distributions
#using CSV
#using StringEncodings
from math import sqrt
from scipy.stats import norm
from scipy.stats import kurtosis
from scipy.stats import skew

import pandas as pd 
import numpy as np 
import statistics 




"""
   return the probability of the performance greater than the given threshold (annual return)
"""
def ProbReturnGreaterThanThreshold(returns,threshold):
   numberOfDays=len(returns)
   if numberOfDays<30:
      print("In order to perform STSE evaluation, you should have at least 30 daily data points, but you got only ",numberOfDays)
      return False
   prob=__estimateProb(returns,(threshold+1)**(1/252)-1)
   return 1-prob
"""
   https://www.google.com/search?q=how+to+obtain+a+distribution+from+another+distribution&oq=how+to+obtain+a+distribution+from+another+distribution&aqs=chrome..69i57.71322j0j4&sourceid=chrome&ie=UTF-8#kpvalbx=_q39vX-3TA9ix5OUPl9Sg4AI30

   y=g(x)= (1+x)^252-1

   Fy(y)=P(Y<=y)
   Y<=y
   g(x)=(1+x)^252-1<=y
   x<=(y+1)^(1/252)-1=expr
   3.Fy(y)=P(Y<=y)=P(x<expr)
   Logo,
   Probabilidade de retorno maior que y=1-Fy(y)=1-P(X<(y+1)^(1/252)-1)
"""

def __estimateProb(returns,limit):
   numberOfDays=len(returns)
   if numberOfDays<30:
      print("In order to perform evaluation, you should have at least 30 daily data points, but you got only ",numberOfDays)
      return False
   if returns==None or len(returns)==0:
      return 0
   smaller=0
   for i in returns:
      if i<=limit:
         smaller=smaller+1
   return smaller/numberOfDays



"""
    calcGeoAvgReturn(returns::Array{Float64}) 
    returns the geometric average of the given serie of returns. 
"""
def calcGeoAvgReturn(returns):
   ret=1
   s=len(returns)
   for  i in range(s):
      ret*=(1+returns[i])
   return ret**(1.0/s)-1

"""
    calcStdDev(x::Array{Float64}) 
    return the standard deviation of a sample
"""
def calcStdDev(x):
   return statistics.stdev(x)


"""
    calculates a serie of return given a serie of prices as argument
    return[i]=price[i]/price[i-1]-1
    the serie of returns has length equal to the price serie lenth minus 1.
"""
def calcReturnsFromPrice(serie):
   x=[]
   if type(serie)==pd.Series:
      for i,valor in serie.iteritems(): # calculates the serie of returns
         x.append(valor)
      y=[]
      for i in range(len(x)-1): # calculates the serie of returns
        y.append(x[i+1]/x[i]-1)
      return y   
   else:
    for i in range(len(serie)-1): # calculates the serie of returns
        x.append(serie[i+1]/serie[i]-1)
    return x


def __calcReturns(serie):
    x=[]
    #print('calcRetursn')
    for i in range(len(serie)-1): # calculates the serie of returns
        x.append(serie[i+1]/serie[i]-1)
        #print(x[i])
    return x


"""
    evaluateEquitySerie(serie,threshold=0.5,riskFree=0.0)
    evaluates a trader performance given its serie of historical equity value 
"""
def evaluateEquitySerie(serie,threshold=0.5,riskFree=0.0):
    if serie is None:
        print("serie should be a list of observed market values of the portfolio, given daily")
        return None
    serie=__calcReturns(serie)
    numberOfDays=len(serie)
    if numberOfDays<30:
        print("In order to perform evaluation, you should have at least 30 data points, but you got only ",numberOfDays)
        return False
    print("\n -----------------------   Backtest Report  ------------------------------- \n")
    print("Total Return (%)={:.2f} in {} bars ".format(calcTotalReturn(serie)*100,numberOfDays))
    print("Average Bar Return (%)={:.2f}  ".format(np.average(serie)*100))
    #print("Annualized Return (%)={:.2f}".format(calcAnnualReturn(serie,numberOfDays)*100))
    print("Std Deviation of returns (%) ={:.4f}".format(calcStdDev(serie)*100))
    #print("Sharpe Ratio={:.4f} ".format(calcSharpeRatio(serie,riskFree)))
    #print("Annualized Sharpe Ratio={:.4f} ".format(calcAnnualSharpeRatio(serie,riskFree,numberOfDays ))),
    """ l1=0
   p1=ProbReturnGreaterThanThreshold(serie,l1)
   l2=0.1
   p2=ProbReturnGreaterThanThreshold(serie,l2)
   l3=0.2
   p3=ProbReturnGreaterThanThreshold(serie,l3)
   
   print("Probability that Annual Return is greater than ({:.1f}%) ={:.2f}%".format(100*l1, 100*p1))
   print("Probability that Annual Return is greater than ({:.1f}%) ={:.2f}%".format(100*l2, 100*p2))
   print("Probability that Annual Return is greater than ({:.1f}%) ={:.2f}%".format(100*l3, 100*p3))"""

    print("\n ----------------------        End of Report     -------------------------------- \n")



"""
    processFile(fileName,numberOfDays)
    process the  "tick-returns CSV file" pointed by fileName and provide several information about the strategy performance. The numberOfDays informs the number of working days in the serie, and it
    can have more or less than a year. One year is assumed to have 252 [working] days. 
"""
def evaluateFile(fileName,threshold=0.5,riskFree=0.0):
  
  # assetSR=calcSharpeRatio(areturns,0)
   cv=pd.read_csv(fileName)

   #rreturns=__calcReturns(cv['equity'])
   #evaluateEquitySerie expectes the equity serie
   evaluateEquitySerie(cv['equity'],threshold,riskFree)


#returns the Total return of a series of returns given of the n first returns
def calcTotalReturn(returns):
   ret=1
   s=len(returns)
   for  i in range(s):
      ret*=(1+returns[i])
   return ret-1


#returns the arithmetic average return of the series of returns given of the n first returns
def calcAvgReturn(returns): 
   sum=float(0)
   s=len(returns)
   for  i in range(s):
      sum+=returns[i]
   return sum/s


def calcAnnualReturn(returns, numberOfDays):
   gReturn=calcTotalReturn(returns)
   return (1+gReturn)**(252.0/numberOfDays)-1



def calcAnnualSharpeRatio(returns, riskfree, numberOfDays):
   # annRet=calcAnnualReturn(returns,numberOfDays)
   # sigma=calcDesvPad(returns) # we suppose sigma stable
   #if(sigma==0) 
   #   print("ERROR! standard deviation equals to zero. In calc Annual SR")
   #   return (annRet-riskfree)
   #end
   #return (annRet-riskfree)/sigma
   # implemented according to paper Andrew W Lo},The Statistics of Sharpe Ratios, journal = {Financial Analysts Journal}, 2003

   return sqrt(252)*calcSharpeRatio(returns,riskfree)


def calcSharpeRatioFromPrice(prices, riskfree): 
   returns=calcReturnsFromPrice(prices)
   return calcSharpeRatio(returns,riskfree)

def calcSharpeRatio(returns, riskfree): 
   avg=calcAvgReturn(returns)
   sigma=calcStdDev(returns)
   if sigma!=0:
       return (avg-riskfree)/sigma
   print("Error!! standard deviation of returns is not suposed to be zero, but it is!!")
   return -1


