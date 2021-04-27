# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

import pandas as pd 
import numpy as np 
import mt5se.mt5se as se
from scipy import stats

def rsi(returns):
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

#	Returns the angular coefficient of linear regression (slope)
#      for a serie of prices in regular intervals
def slope(serie):
    x=np.array(range(len(serie)))
    #y=np.array(serie)
    s=stats.linregress(x,serie)
    return s.slope

# equals to slope
def trend(serie):
    return slope(serie)