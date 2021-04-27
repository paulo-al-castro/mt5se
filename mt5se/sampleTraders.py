# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

import numpy.random as rand
import mt5se as se
import time
import pandas as pd
import numpy as np

class DummyTrader(se.Trader):
    def __init__(self):
        pass

    def setup(self,dbars):
        print('just getting started!')

    def trade(self,ops,dbars):
        orders=[] 
        assets=ops['assets']
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
    def trade(self,bts,dbars):
        assets=dbars.keys()
        asset=list(assets)[0]
        orders=[]
        bars=dbars[asset]
        curr_shares=se.backtest.get_shares(bts,asset)
        # number of shares that you can buy
        free_shares=se.backtest.get_affor_shares(bts,dbars,asset)
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
    def trade(self,bts,dbars):
        assets=dbars.keys()
        orders=[]
        for asset in assets:
            bars=dbars[asset]
            curr_shares=se.backtest.get_shares(bts,asset)
            money=se.backtest.get_balance(bts)/len(assets) # divide o saldo em dinheiro igualmente entre os ativos
            # number of shares that you can buy of asset 
            free_shares=se.backtest.get_affor_shares(bts,dbars,asset,money)
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
 
class SimpleAITrader(se.Trader):  #Decision Tree

    def setup(self,dbars):
        assets=list(dbars.keys())
        if len(assets)!=1:
            print('Error, this trader is supposed to deal with just one asset')
            return None
        bars=dbars[assets[0]]
        timeFrame=10 # it takes into account the last 10 bars
        horizon=1 # it project the closing price for next bar
        target='close' # name of the target column
        ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)

        X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])
        discretizer = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform') 

        ds['target']=se.ai_utils.discTarget(discretizer,ds['target'])
        Y=se.ai_utils.fromDs2NpArray(ds,['target'])

        clf = tree.DecisionTreeClassifier()

        clf = clf.fit(X, Y)
        self.clf=clf

    def trade(self,bts,dbars):
            assets=dbars.keys()
            orders=[]
            timeFrame=10 # it takes into account the last 10 bars
            horizon=1 # it project the closing price for next bar
            target='close' # name of the target column
            for asset in assets:
                curr_shares=se.backtest.get_shares(bts,asset)
                money=se.backtest.get_balance(bts)/len(assets) # divide o saldo em dinheiro igualmente entre os ativos
                free_shares=se.backtest.get_affor_shares(asset,money,dbars)
                # get new information (bars), transform it in X
                bars=dbars[asset]
                #remove irrelevant info
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
        self.clf=dict()
        for asset in assets:
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
            # train model for each asset
            clf = RandomForestClassifier(n_estimators=10)
            clf = clf.fit(X, Y)
            self.clf[asset]=clf
        self.steps=dict()
        self.dbars=dbars
    def trade(self,bts,dbars):
            assets=dbars.keys()
            orders=[]
            timeFrame=10 # it takes into account the last 10 bars
            horizon=1 # it project the closing price for next bar
            target='close' # name of the target column
            for asset in assets:
                #print('Tempo1.1=',datetime.now())
                curr_shares=se.backtest.get_shares(bts,asset)
                #money=se.backtest.get_balance(bts)/len(assets) # divide o saldo em dinheiro igualmente entre os ativos
                if not asset in self.steps:
                    self.steps[asset]=se.get_volume_step(asset)
                free_shares=se.backtest.get_affor_shares(bts,dbars,asset,bts['capital'],self.steps[asset])
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
                p=self.clf[asset].predict([X[-1]])
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

