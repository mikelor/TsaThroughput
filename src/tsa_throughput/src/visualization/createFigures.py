import numpy as np
import pandas as pd

import logging
from dotenv import find_dotenv, load_dotenv
from argparse import ArgumentParser


import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib.dates import (MonthLocator, YearLocator)
from pylab import rcParams

import seaborn as sns
import statsmodels.api as sm
from pathlib import Path

# Based on the article - An End-to-End Project on Time Series Analysis and Forecasting with Python
# https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b



def loadAirports(airports, dfc, dfw, logger):
    # Load the file into a dataframe and checkout the structure
    # Make sure you run this file from the project root folder
    projectDir = Path('.').resolve()
    print(projectDir)

    numAirports = 0

    for airport in airports:
        print(f'Loading data for: {airport}')
        df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.{airport}.csv', header='infer')
        print(f'{airport} loaded.')
        df.fillna(0, inplace=True)
        df.Date = pd.to_datetime(df['Date'])

        # Sum up the amount numbers by day for our graph
        df['Total'] = df.sum(axis = 1, numeric_only=True)
        dfg = df.groupby('Date', as_index=True).agg({'Total': 'sum'})

        # Get the average total of passengers per month
        #y = dfg['Total'].resample('W-MON').mean()
        #y = dfg['Total'].resample('MS').mean()
        dfc[airport] = dfg['Total']
        dfw[airport] = dfg['Total'].resample('W-MON').mean()

        numAirports += 1

    outputFile = f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.Total.csv'
    dfc.to_csv(outputFile, index=True)

# Process Total
#airports.append('Total')
#df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.{airport}.csv', header='infer')
#print(f'{airport} loaded.')
#df.fillna(0, inplace=True)
#df.Date = pd.to_datetime(df['Date'])

# Sum up the amount numbers by day for our graph
#df['Total'] = df.sum(axis = 1, skipna = True)
#dfg = df.groupby('Date', as_index=True).agg({'Total': 'sum'})

# Get the average total of passengers per month
#y = dfg['Total'].resample('W-MON').mean()
#y = dfg['Total'].resample('MS').mean()
#dfc[airport] = dfg['Total']
#dfw[airport] = dfg['Total'].resample('W-MON').mean()


def plotFigure(plt, plotTitle, df, labels, index):

    # Load the file into a dataframe and checkout the structure
    # Make sure you run this file from the project root folder
    projectDir = Path('.').resolve()
    print(f'Plotting: {plotTitle}.{airports[index]}')

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
    plt.savefig(f'{projectDir}/src/tsa_throughput/src/visualization/figures/Figure.{plotTitle}.{airports[index]}.png')
    plt.close(fig)


def plotAirports(airports, dfc, dfw, logger):
    # Figure out the layout for the figure
    # https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
    plotCount = len(airports)

    # Setup to Graph

    rcParams['figure.figsize'] = 18, 8

    plt.rcParams['font.size'] = 13
    plt.rcParams['axes.titlesize']  = 18 # fontsize of the axes title
    plt.rcParams['axes.labelsize']  = 14 # fontsize of the x and y labels
    plt.rcParams['xtick.labelsize'] = 13 # fontsize of the tick labels
    plt.rcParams['ytick.labelsize'] = 13 # fontsize of the tick labels
    plt.rcParams['legend.fontsize'] = 13 # legend fontsize
    plt.rcParams['figure.titlesize'] = 18 # fontsize of the figure title


    numAirports = 0
    for airportCode in airports:
        plotFigure(plt, 'Daily', dfc[airportCode], airports, numAirports)
        plotFigure(plt, 'WeeklyMean', dfw[airportCode], airports, numAirports)

        numAirports += 1


if __name__ == '__main__':
    #  python createFigures.py -a "airportCodes"
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data.')

    parser = ArgumentParser()
    parser.add_argument('-a', '--airportCodes', nargs='?', help = 'The Airport Code')

    args = parser.parse_args()
    
    airports = args.airportCodes.splitlines()

    dfc = pd.DataFrame()
    dfw = pd.DataFrame()
    loadAirports(airports, dfc, dfw, logger)
    plotAirports(airports, dfc, dfw, logger)

    logger.info('Finished making final data set from raw data.')
