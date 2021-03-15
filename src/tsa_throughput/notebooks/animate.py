import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.animation as ani
import matplotlib.dates as mdates

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
print(dfg.head())


#fig = plt.figure()
fig, ax = plt.subplots(figsize=(32, 20))
plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#plt.subplots_adjust(bottom = 0.2, top = 0.9) #ensuring the dates (on the x-axis) fit in the screen


def buildchart(i = int):
	p = plt.plot(dfg.loc[:i,'Date'], dfg.loc[:i, 'SEA SCP 3'])

#animation = ani.FuncAnimation(fig, buildchart, interval=100)

#animation.save(r'/mnt/c/tmp/animation.gif', "imagemagick")

plt.title('SEA TSA Throughput by Date', fontsize=16)
plt.ylabel('Number of Passengers')
plt.xlabel('Date')

plt.grid(True)

colors = ['red', 'green', 'orange', 'blue', 'purple', 'black']
labels = ['SCP 1', 'SCP 2', 'SCP 3', 'SCP 4', 'SCP 5', 'SCP FIS']

def buildAreaChart(plt, df, labels, colors):
	plt.stackplot(df['Date'], df['SEA SCP 1'], df['SEA SCP 2'], df['SEA SCP 3'], df['SEA SCP 4'], df['SEA SCP 5'], df['SEA FIS'], labels=labels, colors=colors)
	return plt

def buildLineChart(plt, df, labels, colors):
	plt.plot(df['Date'], df['SEA SCP 1'], color=colors[0], label=labels[0])
	plt.plot(df['Date'], df['SEA SCP 2'], color=colors[1], label=labels[1])
	plt.plot(df['Date'], df['SEA SCP 3'], color=colors[2], label=labels[2])
	plt.plot(df['Date'], df['SEA SCP 4'], color=colors[3], label=labels[3])
	plt.plot(df['Date'], df['SEA SCP 5'], color=colors[4], label=labels[4])
	plt.plot(df['Date'], df['SEA FIS'],   color=colors[5], label=labels[5])

	return plt

# plt = buildLineChart(plt, dfg, labels, colors)
plt = buildAreaChart(plt, dfg, labels, colors)

plt.legend()
plt.show()
plt.savefig(r'/mnt/c/tmp/figure.jpg')