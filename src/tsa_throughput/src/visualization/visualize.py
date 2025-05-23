import numpy as np
import pandas as pd

import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

import seaborn as sns
import statsmodels.api as sm
from pathlib import Path

# Based on the article - An End-to-End Project on Time Series Analysis and Forecasting with Python
# https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b

# Load the file into a dataframe and checkout the structure
# Make sure you run this file from the project root folder
projectDir = Path('.').resolve()
print(projectDir)

# Read in CSV file, Convert NaN values to 0's
airports = ['Total',
            'ANC', 
            'ATL',
            'AUS',
            'BOI',
            'BZN',
            'DEN',
            'DFW',
            'FLL',
            'LAS', 
            'LAX', 
            'MIA',
            'MCO',
            'MSO',
            'PDX',
            'PHX', 
            'SEA',
            'SJC',
            'SFO',
            'TPA']

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

from pylab import rcParams
rcParams['figure.figsize'] = 18, 8

plt.rc('axes', titlesize=18)     # fontsize of the axes title
plt.rc('axes', labelsize=14)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=13)    # fontsize of the tick labels
plt.rc('ytick', labelsize=13)    # fontsize of the tick labels
plt.rc('legend', fontsize=13)    # legend fontsize
plt.rc('font', size=13)          # controls default text sizes


fig, ax = plt.subplots()
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())


plt.title(f'TSA Throughput By Airport')
plt.xlabel('Date')
plt.ylabel('Passengers')
numAirports = 0
for airport in airports:
    if(numAirports > 0):
        plt.plot(dfw[airport], label=airports[numAirports])

    numAirports += 1

plt.legend(loc="upper right")
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
plt.grid(True)
plt.tight_layout(True)
plt.show()

numAirports = 0
for airport in airports:
    if(numAirports > 0):
        plt.plot(dfc[airport], label=airports[numAirports])

    numAirports += 1

plt.legend(loc="upper right")
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
plt.grid(True)
plt.tight_layout(True)
plt.show()

outputFile = f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.Total.csv'

dfc.to_csv(outputFile, index=True)


# Let's Start Understanding the Time Series

decomposition = sm.tsa.seasonal_decompose(dfw['SEA'], model='additive')
fig = decomposition.plot()
plt.show()


p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))

# Tak says maybe change 12 to 0
#seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
seasonal_pdq = [(x[0], x[1], x[2], 0) for x in list(itertools.product(p, d, q))]

print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(y,
                order=param,
                seasonal_order=param_seasonal,
                enforce_stationarity=False,
                enforce_invertibility=False)

            results = mod.fit()
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

#https://stackoverflow.com/questions/64354366/length-of-endogenous-variable-must-be-larger-the-the-number-of-lags-used
mod = sm.tsa.statespace.SARIMAX(dfw['SEA'],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 0, 12),
#       enforce_stationarity=False,
        enforce_invertibility=False)

results = mod.fit()
print(results.summary().tables[1])

results.plot_diagnostics(figsize=(15, 8))
plt.show()


pred = results.get_prediction(start=pd.to_datetime('2020-01-01'), dynamic=False)
pred_ci = pred.conf_int()
ax = dfw['SEA'].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Date')
ax.set_ylabel('Passengers')
plt.legend()
plt.show()



pred_uc = results.get_forecast(steps=100)
pred_ci = pred_uc.conf_int()
ax = dfw['SEA'].plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Passengers')
plt.legend()
plt.show()


