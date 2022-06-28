# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

import numpy.random as rand
import mt5se as se
import time
import pandas as pd
import numpy as np

class RandomTrader(se.Trader):
    def __init__(self):
        pass

    def setup(self,dbars):
        print('just getting started!')

    def trade(self,dbars):
        orders=[] 
        assets=list(dbars.keys())
        for asset in assets:
            if rand.randint(2)==1:     
                order=se.buyOrder(asset,100)
            else:
            	order=se.sellOrder(asset,100)
            orders.append(order)
        return orders
    
    def ending(self,dbars):
        print('Ending stuff')

 

class MonoAssetTrader(se.Trader):
    def trade(self,dbars):
        assets=dbars.keys()
        asset=list(assets)[0]
        orders=[]
        bars=dbars[asset]
        curr_shares=se.get_shares(asset)
        # number of shares that you can buy
        price=se.get_last(bars)
        free_shares=se.get_affor_shares(asset,price)
        rsi=se.tech.rsi(bars)
        if rsi>=70:   
            order=se.buyOrder(asset,free_shares)
        else:
            order=se.sellOrder(asset,curr_shares)
        if rsi>=70 and free_shares>0: 
            order=se.buyOrder(asset,free_shares)
        elif  rsi<70 and curr_shares>0:
            order=se.sellOrder(asset,curr_shares)
        if order!=None:
                orders.append(order)
        return orders   



class MultiAssetTrader(se.Trader):
    def trade(self,dbars):
        assets=dbars.keys()
        orders=[]
        for asset in assets:
            bars=dbars[asset]
            curr_shares=se.get_shares(asset)
            money=se.get_balance()/len(assets) # divide o saldo em dinheiro igualmente entre os ativos
            # number of shares that you can buy of asset 
            price=se.get_last(bars)
            free_shares=se.get_affor_shares(asset,price,money)
            rsi=se.tech.rsi(bars)
            if rsi>=70 and free_shares>0: 
                order=se.buyOrder(asset,free_shares)
            elif  rsi<70 and curr_shares>0:
                order=se.sellOrder(asset,curr_shares)
            else:
                order=None
            if order!=None:
                orders.append(order)
        return orders   


from sklearn import tree
from sklearn.preprocessing import KBinsDiscretizer
 
class SimpleAITrader(se.Trader):

    def setup(self,dbars):
        assets=list(dbars.keys())
        if len(assets)!=1:
            print('Error, this trader is supposed to deal with just one asset')
            return None
        bars=dbars[assets[0]]
        # remove irrelevant info
        if 'time' in bars:
            del bars['time']
        timeFrame=10 # it takes into account the last 10 bars
        horizon=1 # it project the closing price for next bar
        target='close' # name of the target column
        ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)
        
        X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])
        discretizer = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform') 
        # creates the discrete target
        ds['target']=se.ai_utils.discTarget(discretizer,ds['target'])
        Y=se.ai_utils.fromDs2NpArray(ds,['target'])

        clf = tree.DecisionTreeClassifier()

        clf = clf.fit(X, Y)
        self.clf=clf

    def trade(self,dbars):
            assets=dbars.keys()
            orders=[]
            timeFrame=10 # it takes into account the last 10 bars
            horizon=1 # it project the closing price for next bar
            target='close' # name of the target column
            money=se.get_balance()/len(assets) # shares the balance equally among the assets
            for asset in assets:
                bars=dbars[asset]
                curr_shares=se.get_shares(asset)
                price=se.get_last(bars)
                free_shares=se.get_affor_shares(asset,price,money)
                # get new information (bars), transform it in X
                bars=dbars[asset]
                #remove irrelevant info
                if 'time' in bars:
                    del bars['time']
                # convert from bars to dataset
                ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)
                # Get X fields
                X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])

                # predict the result, using the latest info
                p=self.clf.predict([X[-1]])
                if p==2:
                    #buy it
                    order=se.buyOrder(asset,free_shares)
                elif p==0:
                    #sell it
                    order=se.sellOrder(asset,curr_shares)
                else:
                    order=None
                if order!=None:
                    orders.append(order)
            return orders    



from sklearn.ensemble import RandomForestClassifier
#from sklearn.preprocessing import KBinsDiscretizer

class RandomForestTrader(se.Trader):

    def setup(self,dbars):
        assets=list(dbars.keys())
        if len(assets)!=1:
            print('Error, this trader is supposed to deal with just one asset')
            return None
        bars=dbars[assets[0]]
        # remove irrelevant info
        if 'time' in bars:
            del bars['time']
        timeFrame=10 # it takes into account the last 10 bars
        horizon=1 # it project the closing price for next bar
        target='close' # name of the target column
        ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)
        
        X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])
        discretizer = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform') 
        # creates the discrete target
        ds['target']=se.ai_utils.discTarget(discretizer,ds['target'])
        Y=se.ai_utils.fromDs2NpArray(ds,['target'])

        #clf = tree.DecisionTreeClassifier()
        clf = RandomForestClassifier(n_estimators=10)
        clf = clf.fit(X, Y)
        self.clf=clf

    def trade(self,dbars):
            assets=dbars.keys()
            orders=[]
            timeFrame=10 # it takes into account the last 10 bars
            horizon=1 # it project the closing price for next bar
            target='close' # name of the target column
            money=se.get_balance()/len(assets) # shares the balance equally among the assets
            for asset in assets:
                bars=dbars[asset]
                curr_shares=se.get_shares(asset)
                price=se.get_last(bars)
                free_shares=se.get_affor_shares(asset,price,money)
                # get new information (bars), transform it in X
                bars=dbars[asset]
                #remove irrelevant info
                if 'time' in bars:
                    del bars['time']
                # convert from bars to dataset
                ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)
                # Get X fields
                X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])

                # predict the result, using the latest info
                p=self.clf.predict([X[-1]])
                if p==2:
                    #buy it
                    order=se.buyOrder(asset,free_shares)
                elif p==0:
                    #sell it
                    order=se.sellOrder(asset,curr_shares)
                else:
                    order=None
                if order!=None:
                    orders.append(order)
            return orders    




"""
  Monoaset Monoanalyst Trader, it may be used to evaluate one analyst in respect of one asset
"""
class AnalystTrader(se.Trader):
    def __init__(self,analyst):
        pass
        self.analyst=analyst
        self.dates=[]
        self.current=[]
        self.predicted=[]
        self.actual=[]   

    def setup(self,dbars):
        self.analyst.setup(dbars)
        
    
    def trade(self,ops,dbars):
        orders=[] 
        assets=ops['assets']
        asset=assets[0]
        if len(assets)!=1:
            print('Error!! Analyst trader should manage one and just one asset!!!')
            exit()
        mu=self.analyst.analyze(dbars)# Analysts returns a dictionary with the target prices for each asset
        bars=dbars[asset]
        p=se.get_last(bars) # last price  TODO: esta pegando o preco atual ao inves do seguinte a predicao
        #p_1=bars['close'].iloc[-2]
       #old  actual_return=(p/p_1)**252-1 #actual price #  old (annualized) return from the last cycle (p[t]/p[t-1])^252-1
        self.dates.append(bars['time'].iloc[-1])
        self.current.append(p)
        self.predicted.append(mu[asset])
        self.actual.append(p)
        return orders #AnalystTrader always return no orders!!

    def saveAnalystFile(self):
            print('save analyst file')
            df=pd.DataFrame()
            df['date']=[]
            df['current']=[]
            df['predicted']=[] # predicted (annualized) return 
            df['actual']=[]  # actual (annualized) return from the last cycle (p[t]/p[t-1])^252-1
            #df['price']=[]   #asset price

            for i in range(len(self.dates)):
                df.loc[i]=[self.dates[i],self.current[i],self.predicted[i],self.actual[i]]
            df.to_csv('analyst_performance.csv') 



