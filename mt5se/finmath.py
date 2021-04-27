# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17

import pandas as pd 
import numpy as np 
from math import sqrt
import statistics 
"""
    calcGeoAvgReturn(returns::Array{Float64} [,n::Int] ) 
 returns the geometric average return of the series of the n first returns returns. If n is not informed the whole array is used 
"""
def calcGeoAvgReturn(returns,n=None):
   ret=1
   if n==None:
      n=len(returns)
   for  i in range(n): 
      ret*=(1+returns[i])
   
   return ret**(1.0/n)-1

 

 
"""
    calcTotalReturn(returns::Array{Float64}) 
   returns the Total return of a series of returns
   If the size is provided it considers just 'size' more recent (more to the right) returns
"""
def calcTotalReturn(returns,size=None):
   ret=1
   s=len(returns)
   if size==None:
      size=0
   elif size<s:
      size=s-size
   else: 
      size=0 # it gets in maximum the return of the total number of elements
   for  i in range(s-1,size-1,-1): 
      ret*=(1+returns[i])
   return ret-1

def changedSignal(returns):
   s=len(returns)
   if s==None or s==1:
      return False
   for i in range(s-1):
      if returns[i]*returns[i+1]<0:
         return True
   return False


"""
    calcAvgReturn(returns::Array{Float64}) 
    returns the arithmetic average return of the series of returns
"""
def calcAvgReturn(returns):
   sum=float(0)
   s=len(returns)
   for  i in range(s): 
      sum+=returns[i]
   return sum/s


"""
    calcAnnualReturn(returns::Array{Float64}, numberOfDays)  
    returns the equivalent annual return for the given serie of returns. The numberOfDays informs the number of working days in the serie, and it
         can have more or less than a year. One year is assumed to have 252 [working] days.
"""
def calcAnnualReturn(returns, numberOfDays):
   gReturn=calcTotalReturn(returns)
   return (1+gReturn)**(252.0/numberOfDays)-1



"""
    calcAnnualSR(returns::Array{Float64}, riskfree, numberOfDays)
    returns the equivalent annual sharpe ratio (SR) for the given serie of returns and risk free rate. The numberOfDays informs the number of working days in the serie, and it
         can have more or less than a year. One year is assumed to have 252 [working] days.
"""
def calcAnnualSR(returns, riskfree, numberOfDays):
   # implemented according paper: Andrew W Lo},The Statistics of Sharpe Ratios, journal = {Financial Analysts Journal}, 2003

   return sqrt(252)*calcSR(returns,riskfree)


"""
    calcStdDev(x::Array{Float64}) 
    return the standard deviation of a sample
"""
def calcStdDev(x):
   return statistics.stdev(x)


"""
    calcSR(returns::Array{Float64}, riskfree)
    returns the Sharpe ratio (SR) for the given serie of returns and risk free rate. 
"""
def calcSR(returns, riskfree):
   avg=calcAvgReturn(returns)
   sigma=calcStdDev(returns)
   if sigma!=0:
       return (avg-riskfree)/sigma
   return -1



"""
    calculates a serie of return given a serie of prices as argument
    return[i]=price[i]/price[i-1]-1
    the serie of returns has length equal to the price serie lenth minus 1.
"""
def calcReturns(serie):
    x=[]
    for i in range(len(serie)-1): # calculates the serie of returns
        x.append(serie[i+1]/serie[i]-1)
    return x


"""
   gives the standard deviation of returns given a serie of prices
"""
def calcStdDevFromPrice(x):
    returns=calcReturns(x)
    return calcStdDev(returns)

"""
   gives the average returns given a serie of prices
"""
def calcAvgReturnFromPrice(x):
    returns=calcReturns(x)
    return calcAvgReturn(returns)

