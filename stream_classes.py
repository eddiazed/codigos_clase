# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 09:10:59 2020

@author: Meva
"""

import numpy as np
import pandas as pd
import matplotlib as mpl
import scipy
import importlib
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, chi2, linregress

# import our own files and reload
import stream_functions
importlib.reload(stream_functions)


class jarque_bera_test():
    
    def __init__(self, x, x_str):
        self.returns = x
        self.str_name = x_str
        self.size = len(x) # size of returns
        self.round_digits = 4
        self.mean = 0.0
        self.std = 0.0
        self.skew = 0.0
        self.kurt = 0.0
        self.median = 0.0
        self.var_95 = 0.0
        self.cvar_95 = 0.0
        self.sharpe = 0.0
        self.jarque_bera = 0.0
        self.p_value = 0.0
        self.is_normal = 0.0

    def compute(self):
        self.mean = np.mean(self.returns)
        self.std = np.std(self.returns) # volatility
        self.skew = skew(self.returns)
        self.kurt = kurtosis(self.returns) # excess kurtosis
        self.sharpe = self.mean / self.std * np.sqrt(252) # annualised
        self.median = np.median(self.returns)
        self.var_95 = np.percentile(self.returns,5)
        self.cvar_95 = np.mean(self.returns[self.returns <= self.var_95])
        self.jarque_bera = self.size/6*(self.skew**2 + 1/4*self.kurt**2)
        self.p_value = 1 - chi2.cdf(self.jarque_bera, df=2)
        self.is_normal = (self.p_value > 0.05) # equivalently jb < 6

    def __str__(self):
        str_self = self.str_name + ' | size ' + str(self.size) + '\n' + self.plot_str()
        return str_self
      
    def plot_str(self):
        plot_str = 'mean ' + str(np.round(self.mean,self.round_digits))\
            + ' | median ' + str(np.round(self.median,self.round_digits))\
            + ' | std dev ' + str(np.round(self.std,self.round_digits))\
            + ' | skewness ' + str(np.round(self.skew,self.round_digits)) + '\n'\
            + 'kurtosis ' + str(np.round(self.kurt,self.round_digits))\
            + ' | Sharpe ratio ' + str(np.round(self.sharpe,self.round_digits))\
            + ' | VaR 95% ' + str(np.round(self.var_95,self.round_digits))\
            + ' | CVaR 95% ' + str(np.round(self.cvar_95,self.round_digits)) + '\n'\
            + 'Jarque Bera ' + str(np.round(self.jarque_bera,self.round_digits))\
            + ' | p-value ' + str(np.round(self.p_value,self.round_digits))\
            + ' | is normal ' + str(self.is_normal)
        return plot_str
    
    
class capm_manager():
    
    def __init__(self, ric, benchmark):
        self.nb_decimals = 4
        self.ric = ric
        self.benchmark = benchmark
        self.x = []
        self.y = []
        self.t = pd.DataFrame()
        self.alpha = 0.0
        self.beta = 0.0
        self.p_value = 0.0
        self.null_hypothesis = False
        self.r_value = 0.0
        self.r_squared = 0.0
        self.predictor_linreg = []
        
    def __str__(self):
        str_self = '__str__ not yet defined, next course please'
        return str_self
        
    def load_timeseries(self):
        # load timeseries and synchronise them
        self.x, self.y, self.t = stream_functions.synchronise_timeseries(self.ric, self.benchmark)
    
    def compute(self):
        # linear regression of ric with respect to benchmark
        slope, intercept, r_value, p_value, std_err = linregress(self.x,self.y)
        self.beta = np.round(slope, self.nb_decimals)
        self.alpha = np.round(intercept, self.nb_decimals)
        self.p_value = np.round(p_value, self.nb_decimals) 
        self.null_hypothesis = p_value > 0.05 # p_value < 0.05 --> reject null hypothesis
        self.r_value = np.round(r_value, self.nb_decimals) # correlation coefficient
        self.r_squared = np.round(r_value**2, self.nb_decimals) # pct of variance of y explained by x
        self.predictor_linreg = self.alpha + self.beta*self.x
        
    def scatterplot(self):
        # scatterplot of returns
        str_title = 'Scatterplot of returns' + '\n'\
            + 'Linear regression | ric ' + self.ric\
            + ' | benchmark ' + self.benchmark + '\n'\
            + 'alpha (intercept) ' + str(self.alpha)\
            + ' | beta (slope) ' + str(self.beta) + '\n'\
            + 'p-value ' + str(self.p_value)\
            + ' | null hypothesis ' + str(self.null_hypothesis) + '\n'\
            + 'r-value ' + str(self.r_value)\
            + ' | r-squared ' + str(self.r_squared)
        plt.figure()
        plt.title(str_title)
        plt.scatter(self.x,self.y)
        plt.plot(self.x, self.predictor_linreg, color='green')
        plt.ylabel(self.ric)
        plt.xlabel(self.benchmark)
        plt.grid()
        plt.show()