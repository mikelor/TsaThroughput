import numpy as np
import pandas as pd

import itertools

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

import seaborn as sns

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

from pathlib import Path

# Based on this article - ARIMA Model Python Example — Time Series Forecasting
# https://towardsdatascience.com/machine-learning-part-19-time-series-and-autoregressive-integrated-moving-average-model-arima-c1005347b0d7


def get_stationarity(timeseries):
    
    # rolling statistics
    rolling_mean = timeseries.rolling(window=14).mean()
    rolling_std = timeseries.rolling(window=14).std()
    
    # rolling statistics plot
    original = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolling_mean, color='red', label='Rolling Mean')
    std = plt.plot(rolling_std, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show()
    plt.savefig('test.png')
    
    # Dickey–Fuller test:
    result = adfuller(timeseries)
    print('ADF Statistic: {}'.format(result[0]))
    print('p-value: {}'.format(result[1]))
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))


# Load the file into a dataframe and checkout the structure
projectDir = Path('.').resolve().parents[1]

# Read in CSV file, Convert NaN values to 0's
airports = [ 'SEA' ]

numAirports = 0
dfc = pd.DataFrame()
for airport in airports:
    
    df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.{airport}.csv', header='infer')
    df.fillna(0, inplace=True)
    df.Date = pd.to_datetime(df['Date'])

    # Sum up the amount numbers by day for our graph
    df['Total'] = df.sum(axis = 1, skipna = True)
    dfg = df.groupby('Date', as_index=True).agg({'Total': 'sum'})

    # Get the average total of passengers per month
    #y = dfg['Total'].resample('W-MON').mean()
    #y = dfg['Total'].resample('MS').mean()
    if(numAirports < 1):
        dfc = dfg
        dfw = dfg['Total'].resample('MS').mean()
    else:
        dfc[airport] = dfg['Total']
        dfw[airport] = dfg['Total'].resample('MS').mean()

    numAirports += 1




df_log = np.log(dfg)
#plt.plot(df_log)
rolling_mean = df_log.rolling(window=12).mean()
df_log_minus_mean = df_log - rolling_mean
df_log_minus_mean.dropna(inplace=True)
get_stationarity(df_log_minus_mean)
