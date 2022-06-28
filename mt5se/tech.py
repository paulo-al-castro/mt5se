# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

import pandas as pd 
import numpy as np 
import mt5se.mt5se as se
from scipy import stats

def rsi(returns):
    """
    	Returns the RSI (Relative Strengh Index) of a given serie of returns.
            if the parameter is a pandas.DataFrame it uses the function mt5se.get_return() to get the
            serie of returns
    """
    if type(returns)==pd.core.frame.DataFrame:
        returns=se.get_returns(returns)
    u=0.0
    uc=0
    d=0.0
    dc=0
    for r in returns:
        if r>=0:
            u=u+r
            uc=uc+1
        else:
            d=d+abs(r)
            dc=dc+1
    if uc>0:
        u=u/uc
    if dc>0:
        d=d/dc   
    if d==0:
        d=1.0
    ifr=100*( 1 - 1/(1+u/d))
    return ifr


def slope(serie):
    """
    	Returns the angular coefficient of linear regression (slope)
          for a serie of prices in regular intervals
    """
    x=np.array(range(len(serie)))
    #y=np.array(serie)
    s=stats.linregress(x,serie)
    return s.slope

# equals to slope
def trend(serie):
    """
      	Returns the angular coefficient of linear regression (slope)
          for a serie of prices in regular intervals 
          Same as function slope()
    """
    return slope(serie)

def ma(serie,length=10):
    """"
        Returns the moving average of lenght points.
            In the fist points (0-length), it calculcates the average from 0 to index.
            So, the first ma is equal to the first number of the serie, the second is the average between the first and second numbers of the serie, and so on
    """
    mov_avg=[]
    for i in range(len(serie)):
        if i <=length:
            mov_avg.append(np.mean(serie[0:i+1]))
        else:
            mov_avg.append(np.mean(serie[i-9:i+1]))
    return mov_avg

    