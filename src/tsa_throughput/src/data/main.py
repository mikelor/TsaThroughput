#packages
import json
import os
import pandas
from pandas import json_normalize
import argparse

import warnings
import itertools
import numpy as np
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['text.color'] = 'k'

print(f'Current Working Directory is: {os.getcwd()}\n')


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", help = "The full path and filename for the input file")
parser.add_argument("-o", "--outputFile", help = "The full path and filename for the output file")


args = parser.parse_args()
inputFile = args.inputFile
outputFile = args.outputFile

#load json file
with open(inputFile) as f:
    data = json.load(f)

#normalize and store in df
df = pandas.json_normalize(data,
                       record_path=['Airports', 'Days', 'Checkpoints', 'Hours'],
                       meta=[
                           ['Airports', 'Days', 'Checkpoints', 'CheckpointName'],
                           ['Airports', 'Days', 'Date'],
                           ['Airports', 'AirportCode'],
                           ['Airports', 'AirportName'],
                           ['Airports', 'City'],
                           ['Airports', 'State'],
                       ],
                       )
#Convert to datetime and get time
df['Hour'] = pandas.to_datetime(df['Hour'], errors='coerce')
df['Hour'] = df['Hour'].dt.time

#Convert to datetime and get date
df['Airports.Days.Date'] = pandas.to_datetime(df['Airports.Days.Date'], errors='coerce')
df['Airports.Days.Date'].dt.date

#load json file
inputFile = './data/raw/tsa/throughput/tsa-throughput-november-22-2020-to-november-28-2020.json'
with open(inputFile) as f:
    data = json.load(f)

#normalize and store in df
dfa = pandas.json_normalize(data,
                       record_path=['Airports', 'Days', 'Checkpoints', 'Hours'],
                       meta=[
                           ['Airports', 'Days', 'Checkpoints', 'CheckpointName'],
                           ['Airports', 'Days', 'Date'],
                           ['Airports', 'AirportCode'],
                           ['Airports', 'AirportName'],
                           ['Airports', 'City'],
                           ['Airports', 'State'],
                       ],
                       )
#Convert to datetime and get time
dfa['Hour'] = pandas.to_datetime(dfa['Hour'], errors='coerce')
dfa['Hour'] = dfa['Hour'].dt.time

#Convert to datetime and get date
dfa['Airports.Days.Date'] = pandas.to_datetime(dfa['Airports.Days.Date'], errors='coerce')
dfa['Airports.Days.Date'].dt.date

df = df.append(dfa)
print(df)
print(df.shape)

#New dataframe with limited columns
df2 = df.reindex(columns= ['Airports.Days.Date','Hour','Airports.AirportCode','Airports.AirportName','Airports.City','Airports.State','Amount'])
#print(df2)

#Filter only SEA
isSea = df['Airports.AirportCode'] == 'SEA'
#print(isSea.head())

#Create data frame with only SEA
df_sea = df[isSea]
#print(df_sea.shape)

#export normalized JSON to CSV file
#csv_export = df_pivot.to_csv(outputFile, index=False)

throughput = df_sea.groupby('Airports.Days.Date')['Amount'].sum()
#throughput.plot(figsize=(10, 6))
#plt.show()
#print(throughput.head)

#from pylab import rcParams
#rcParams['figure.figsize'] = 10, 6
#decomposition = sm.tsa.seasonal_decompose(throughput, model='additive')
#fig = decomposition.plot()
#plt.show()

df_log = np.log(throughput)
plt.plot(df_log)

def get_stationarity(timeseries):
    
    # rolling statistics
    rolling_mean = timeseries.rolling(window=12).mean()
    rolling_std = timeseries.rolling(window=12).std()
    
    # rolling statistics plot
    original = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolling_mean, color='red', label='Rolling Mean')
    std = plt.plot(rolling_std, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    
    # Dickey–Fuller test:
    result = adfuller(throughput)
    print('ADF Statistic: {}'.format(result[0]))
    print('p-value: {}'.format(result[1]))
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))

rolling_mean = df_log.rolling(window=12).mean()
df_log_minus_mean = df_log - rolling_mean
df_log_minus_mean.dropna(inplace=True)
get_stationarity(df_log_minus_mean)