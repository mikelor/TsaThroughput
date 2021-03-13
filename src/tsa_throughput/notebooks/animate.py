import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.animation as ani
from pathlib import Path

# Load the file into a dataframe and checkout the structure
projectDir = Path('.').resolve()
df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.SEA.csv', header='infer')
df = df.rename(columns = {'Airports.Days.Date' : 'Date', 'SEA FIS Checkpoint' : 'SEA FIS'}, inplace=False)
df.Date = pd.to_datetime(df['Date'])
dfg = df.groupby('Date', as_index=False).agg({"SEA SCP 3": "sum"})
print(dfg.head())


# SCP 1              ->
# SCP 2			     -> SEA South Checkpoint		
# SCP 3              -> SEA Central Checkpoint     
# SCP 4	             -> SEA Charlie Checkpoint    
# SCP 5              -> SEA North Checkpoint ()
# SEA FIS Checkpoint -> SEA Offsite

#fig = plt.figure()
fig, ax = plt.subplots(figsize=(16, 10))
plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values
plt.subplots_adjust(bottom = 0.2, top = 0.9) #ensuring the dates (on the x-axis) fit in the screen
plt.ylabel('Amount')
plt.xlabel('Dates')

def buildchart(i = int):
	p = plt.plot(dfg.loc[:i,'Date'], dfg.loc[:i, 'SEA SCP 3'])
	for i in range(0, 1):
		p[i].set_color('red')

animation = ani.FuncAnimation(fig, buildchart, interval=200)

animation.save(r'/mnt/c/tmp/animation.gif', "imagemagick")
plt.show()