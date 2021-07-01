import numpy as np
import pandas as pd

import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib.dates import (MonthLocator, YearLocator)

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
airports = ['All',
            'ANC', 
            'ATL',
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
            'TPA',
            'Total']

numAirports = 0
dfc = pd.DataFrame()
dfw = pd.DataFrame()
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
    dfc[airport] = dfg['Total']
    dfw[airport] = dfg['Total'].resample('W-MON').mean()

    numAirports += 1

outputFile = f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.Total.csv'
dfc.to_csv(outputFile, index=True)

from pylab import rcParams
rcParams['figure.figsize'] = 18, 8

plt.rc('axes', titlesize=18)     # fontsize of the axes title
plt.rc('axes', labelsize=14)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=13)    # fontsize of the tick labels
plt.rc('ytick', labelsize=13)    # fontsize of the tick labels
plt.rc('legend', fontsize=13)    # legend fontsize
plt.rc('font', size=13)          # controls default text sizes


def plotFigure(plt, plotTitle, df, labels, index):
    fig, ax = plt.subplots()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())  
    plt.xlabel('Date')
    plt.ylabel('Passengers')

    plt.title(f'TSA Throughput ({plotTitle}) for {labels[index]}')

    plt.plot(df, label=labels[index])

    plt.legend(loc="upper right")
    plt.xticks(rotation=45, ha="right")
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.xaxis.set_major_locator(MonthLocator())
    plt.grid(True)
    plt.savefig(f'{projectDir}/src/tsa_throughput/src/visualization/figures/Figure.{plotTitle}.{airports[numAirports]}.png')
    plt.close(fig)


# Figure out the layout for the figure
# https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
plotCount = len(airports)

numAirports = 0
for airport in airports:

    plotFigure(plt, 'Daily', dfc[airport], airports, numAirports)
    plotFigure(plt, 'WeeklyMean', dfw[airport], airports, numAirports)

    numAirports += 1




