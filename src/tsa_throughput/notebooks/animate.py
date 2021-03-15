import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.animation as ani
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from pathlib import Path

# Load the file into a dataframe and checkout the structure
projectDir = Path('.').resolve()

# Read in CSV file, Convert NaN values to 0's
df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.SEA.csv', header='infer')
df.fillna(0, inplace=True)
df = df.rename(columns = {'Airports.Days.Date' : 'Date', 'SEA FIS Checkpoint' : 'SEA FIS'}, inplace=False)
df.Date = pd.to_datetime(df['Date'])


# Checkpoint names have changed over time, so we need to consolidate to new names
# SEA Offsite Checkpoint -> SCP 1
# SEA South Checkpoint   -> SCP 2		
# SEA Central Checkpoint -> SCP 3    
# SEA Charlie Checkpoint -> SCP 4   
# SEA North Checkpoint   -> SCP 5
# SEA FIS Checkpont      -> SEA FIS Checkpoint
df['SEA SCP 1'] = df['SEA SCP 1'] + df['SEA Offsite Checkpoint']
df['SEA SCP 2'] = df['SEA SCP 2'] + df['SEA South Checkpoint']
df['SEA SCP 3'] = df['SEA SCP 3'] + df['SEA Central Checkpoint']
df['SEA SCP 4'] = df['SEA SCP 4'] + df['SEA Charlie Checkpoint']
df['SEA SCP 5'] = df['SEA SCP 5'] + df['SEA North Checkpoint']

# Sum up the amount numbers by day for our graph
dfg = df.groupby('Date', as_index=False).agg({'SEA SCP 1': 'sum', 'SEA SCP 2': 'sum', 'SEA SCP 3': 'sum', 'SEA SCP 4': 'sum', 'SEA SCP 5': 'sum', 'SEA FIS': 'sum'})


fig, ax = plt.subplots(figsize=(32, 20))

def setupChart(plt):
	plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values
	
	ax = plt.gca()
	
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))

	ax.yaxis.set_major_locator(ticker.MultipleLocator(5000))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(1000))

	plt.title('SEA TSA Throughput by Date', fontsize=24)
	plt.ylabel('Number of Passengers', fontsize=16)
	plt.xlabel('Date', fontsize=16)

	plt.grid(True)

	return plt

def buildAreaChart(plt, df, labels, colors):
	plt.stackplot(df['Date'], df[labels[0]], df[labels[1]], df[labels[2]], df[labels[3]], df[labels[4]], df[labels[5]], labels=labels, colors=colors)
	return plt

def buildLineChart(plt, df, labels, colors):
	for i in range(0, len(labels)):
		plt.plot(df['Date'], df[labels[i]], color=colors[i], label=labels[i])

	return plt

def animateChart(i = int):
	p = plt.plot(dfg.loc[:i,'Date'], dfg.loc[:i, 'SEA SCP 3'])

colors = ['red', 'green', 'blue']
labels = ['SEA SCP 3', 'SEA SCP 4', 'SEA SCP 5']
plt = setupChart(plt)
animation = ani.FuncAnimation(plt.gcf(), animateChart, interval=50)
plt.show()
animation.save(r'/mnt/c/tmp/animation.gif', "ffmpeg")

# plt = buildLineChart(plt, dfg, labels, colors)
#colors = ['red', 'green', 'orange', 'blue', 'purple', 'black']
#labels = ['SEA SCP 1', 'SEA SCP 2', 'SEA SCP 3', 'SEA SCP 4', 'SEA SCP 5', 'SEA FIS']
colors = ['red', 'green', 'blue']
labels = ['SEA SCP 3', 'SEA SCP 4', 'SEA SCP 5']
plt = setupChart(plt)
plt.stackplot(dfg['Date'], dfg[labels[0]], dfg[labels[1]], dfg[labels[2]], labels=labels, colors=colors)
plt.legend()
plt.show()
plt.savefig(r'/mnt/c/tmp/figure1-AreaSCP345.jpg')

plt.clf()
colors = ['red', 'green', 'blue']
labels = ['SEA SCP 3', 'SEA SCP 4', 'SEA SCP 5']
plt = setupChart(plt)
plt = buildLineChart(plt, dfg, labels, colors)
plt.legend()
plt.show()
plt.savefig(r'/mnt/c/tmp/figure2-LineSCP345.jpg')

plt.clf()
colors = ['red', 'green', 'blue']
labels = ['SEA SCP 1', 'SEA SCP 2', 'SEA FIS']
plt = setupChart(plt)
plt = buildLineChart(plt, dfg, labels, colors)
plt.legend()
plt.show()
plt.savefig(r'/mnt/c/tmp/figure3-LineSCP12FIS.jpg')

