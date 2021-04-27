import mt5se as se
import pandas as pd
import numpy as np


## Defines the RandomForestAnalyst
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import KBinsDiscretizer


class RsiAnalyst(se.Analyst):
    def setup(self,dbars):
        assets=list(dbars.keys())
        df=se.get_close_prices_from_dbars(assets,dbars)
        # train model
        self.mu = se.mean_historical_return(df)
        self.alpha=0.5
        self.dbars=dbars


    def analyze(self,dbars):
        assets=dbars.keys()
        returns=dict()
        alpha=self.alpha
        for asset in assets:
            bars=dbars[asset]
            # number of shares that you can buy of asset 
            rsi=se.tech.rsi(bars)
            er=self.mu[asset]
            if rsi>=70: 
                exp_ret=er+alpha*abs(er)          
            elif  rsi<70:
                exp_ret=er-alpha*abs(er)                  
            returns[asset]=exp_ret
        return returns    

class MAAnalyst(se.Analyst):
    def setup(self,dbars):
        assets=list(dbars.keys())
        df=se.get_close_prices_from_dbars(assets,dbars)
        # train model
        mu = se.mean_historical_return(df)
        self.alpha=0.5
        self.mu=mu
        self.period=10

    def analyze(self,dbars):
        assets=dbars.keys()
        returns=dict()
        for asset in assets:
            bars=dbars[asset]
            # number of shares that you can buy of asset 
            er=self.mu[asset]
            m=np.mean(bars['close'][-self.period:])
            if se.tech.trend(bars['close'])>0 and bars['close'].iloc[-1]<m:
                exp_ret=er+self.alpha*abs(er)
            elif se.tech.trend(bars['close'])<0 and m<bars['close'].iloc[-1]:
                exp_ret=er-self.alpha*abs(er)
            else:
                exp_ret=None
            returns[asset]=exp_ret
        return returns  


class MACDAnalyst(se.Analyst):
    def setup(self,dbars):
        self.period=26
        self.short_period=12
        self.signal=9
        assets=list(dbars.keys())
        df=se.get_close_prices_from_dbars(assets,dbars)
        if len(df)<self.period+self.signal:
            print('The setup period (prestart-start) should have at least ',self.period+self.signal,' data points')
            return
        # train model
        mu = se.mean_historical_return(df)
        self.alpha=0.5
        self.dbars=dbars
        self.mu=mu
        self.lastMacdUnderSignal=True

    def analyze(self,dbars): #recebe um numero de barras igual a prestart-start porem ja roladas
        assets=dbars.keys()
        returns=dict()
        MacdUnderSignal=True
        lastMacdUnderSignal=True
        alpha=self.alpha
        for asset in assets:
            #self.dbars[asset]=se.roll_bars(self.dbars[asset],ndbars[asset])
            bars=dbars[asset]
            # number of shares that you can buy of asset 
            #m=np.mean(bars['close'])
            longer=np.mean(bars['close'][-self.period:])
            shorter=np.mean(bars['close'][-self.short_period:])
            signaling=np.mean(bars['close'][-self.signal:])
            er=self.mu[asset]
            if((shorter-longer)>signaling):
                MacdUnderSignal=False
            else:
                MacdUnderSignal=True
            if(not MacdUnderSignal and  lastMacdUnderSignal): # alta: compra
    	        exp_ret=er+alpha*abs(er)
    	        print('buy ',asset,' expr_r=', exp_ret)
            elif(MacdUnderSignal and  not lastMacdUnderSignal): #baixa: vende
                exp_ret=er-alpha*abs(er)
                print('sell ',asset,' expr_r=',exp_ret)
            else: # indefinido faz nada
                exp_ret=None
                print('Nothing ',asset,' expr_r=',exp_ret)  
            lastMacdUnderSignal= MacdUnderSignal  	        
            returns[asset]=exp_ret
        return returns  


class RandomForestAnalyst(se.Analyst):
    def setup(self,dbars):
        assets=list(dbars.keys())
        df=se.get_close_prices_from_dbars(assets,dbars)
        mu = se.mean_historical_return(df)
        self.clf=dict()
        for asset in assets:
            bars=dbars[assets[0]]
            bars=bars.copy()
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
            #print('ds=',ds)
            ds['target']=se.ai_utils.discTarget(discretizer,ds['target'])
            Y=se.ai_utils.fromDs2NpArray(ds,['target'])
            # train model for each asset
            clf = RandomForestClassifier(n_estimators=10)
            clf = clf.fit(X, Y)
            self.clf[asset]=clf
        self.steps=dict()
        self.alpha=0.5
        self.dbars=dbars
        self.mu=mu
    def analyze(self,dbars):
            assets=dbars.keys()
            returns=dict()
            timeFrame=10 # it takes into account the last 10 bars
            horizon=1 # it project the closing price for next bar
            target='close' # name of the target column
            for asset in assets:
                #print('Tempo1.1=',datetime.now())
                # get new information (bars), transform it in X
                bars=dbars[asset]
                bars=bars.copy()
                #remove irrelevant info
                if 'time' in bars:
                    del bars['time']
                # convert from bars to dataset
                ds=se.ai_utils.bars2Dataset(bars,target,timeFrame,horizon)
                # Get X fields
                X=se.ai_utils.fromDs2NpArrayAllBut(ds,['target'])
                # predict the result, using the latest info
                p=self.clf[asset].predict([X[-1]])
                er=self.mu[asset]
                if p==2:
                    exp_ret=er+self.alpha*abs(er)      #buy it
                    print("buy ",asset)
                elif p==0:
                    #sell it
                    exp_ret=er-self.alpha*abs(er)
                    print("sell ",asset)
                else:
                    exp_ret=None
                    print("do nothing ",asset)
                returns[asset]=exp_ret
            return returns    


def ensembleAnalyses(analysts_mus,mu):
    expected_returns=dict()
    assets=analysts_mus[0].keys()
    for asset in assets:
        count=0
        expected_returns[asset]=0
        for i in range(len(analysts_mus)): # gets expected return of each analyst
            if analysts_mus[i][asset]!=None:
                expected_returns[asset]=expected_returns[asset]+analysts_mus[i][asset]
                count=count+1
        if count>0:
            expected_returns[asset]=expected_returns[asset]/count
        else:
            expected_returns[asset]=0 #mu[asset] # if no analyst informed anything uses zero instead of the historical value
    return pd.Series(expected_returns)


