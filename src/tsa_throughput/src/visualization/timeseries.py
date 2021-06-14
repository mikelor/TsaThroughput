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
    
    # Dickey–Fuller test:
    result = adfuller(timeseries)
    print('ADF Statistic: {}'.format(result[0]))
    print('p-value: {}'.format(result[1]))
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))


# Load the file into a dataframe and checkout the structure
# Make sure you run this file from the project root folder
projectDir = Path('.').resolve()

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


p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

#Grid search to find the optimal set of parameters for model. Runs every set of parameters. The lowest AIC indictates the optimal set.

# for param in pdq:
#     for param_seasonal in seasonal_pdq:
#         try:
#             mod = sm.tsa.statespace.SARIMAX(dfg,
#                                             order=param,
#                                             seasonal_order=param_seasonal,
#                                             enforce_stationarity=False,
#                                             enforce_invertibility=False)

#             results = mod.fit()

#             print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
#         except:
#             continue

mod = sm.tsa.statespace.SARIMAX(dfg,
                                order=(1, 1, 1),
                                seasonal_order=(1, 0, 1, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

#print(results.summary().tables[1])

#Diagnostics to check for anything unusual.
results.plot_diagnostics(figsize=(10, 5))
#plt.show()

#Validate forecast by checking predicted throughput to actual throughput. Plot starts in 2018, forecast starts at 2020.
pred = results.get_prediction(start=pd.to_datetime('2020-01-01'), dynamic=False)
pred_ci = pred.conf_int()
ax = dfg['2018':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(10, 5))
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Date')
ax.set_ylabel('Throughput')
plt.legend()
#plt.show()

#Vizualizing forecast
pred_uc = results.get_forecast(steps=100)
pred_ci = pred_uc.conf_int()
ax = dfg.plot(label='observed', figsize=(10, 5))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Throughput')
plt.legend()
plt.show()

#Prints forecasted values
print(pred_uc.predicted_mean)