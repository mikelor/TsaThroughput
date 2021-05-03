import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.animation as ani
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from pathlib import Path

from dotenv import find_dotenv, load_dotenv
import logging
from pathlib import Path
from argparse import ArgumentParser

def createAnimation(projectDir, airport, outputDir, logger):
	airportString = 'All'
	if(airport is not None):
		airportString = airport

	logger.info(f'Creating Chart Animation For {airportString}.')

	# Read in CSV file, Convert NaN values to 0's
	df = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.{airportString}.csv', header='infer')

	df.fillna(0, inplace=True)
	df.Date = pd.to_datetime(df['Date'])

	# Sum up the amount numbers by day for our graph
	df['Total'] = df.sum(axis = 1, skipna = True)
	dfg = df.groupby('Date', as_index=False).agg({'Total': 'sum'})

	fig, ax = plt.subplots(figsize=(32,10))
	
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))

	ax.yaxis.set_major_locator(ticker.MaxNLocator())
	ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

	ax.set_ylim(0,dfg['Total'].max())
	ax.set_xlim(dfg['Date'].min(),dfg['Date'].max())

	plt.title(f'{airportString} TSA Throughput by Date', fontsize=24)

	plt.ylabel('Number of Passengers', fontsize=16)
	plt.xlabel('Date', fontsize=16)
	plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values

	plt.grid(True)
	plt.tight_layout(True)

	animation = ani.FuncAnimation(plt.gcf(), animateChart, fargs=[dfg, logger], frames=len(dfg), interval=100)
	animation.save(f'{outputDir}/TsaThroughput.{airportString}.mp4', writer='ffmpeg')
	logger.info(f'Finished Processing Chart Animation for {airportString}')

def animateChart(i, df, logger):
	p = plt.plot(df.loc[:i,'Date'], df.loc[:i, 'Total'], color='b')
	if(i % 10 == 0):
		logger.info(f'{i} of {len(df)} data points processed')

if __name__ == '__main__':
	#  python animate.py -a LAS -o /mnt/c/tmp 

	log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(level=logging.INFO, format=log_fmt)

	# not used in this stub but often useful for finding various files
	project_dir = Path('.').resolve().parents[0]

	# find .env automagically by walking up directories until it's found, then
	# load up the .env entries as environment variables
	load_dotenv(find_dotenv())

	logger = logging.getLogger(__name__)


	parser = ArgumentParser()
	parser.add_argument('-a', '--airportCode', nargs='?',  help = 'The Airport Code to filter dataset by')
	parser.add_argument('-o', '--outputDir',               help = 'The output directory to write the file')

	args = parser.parse_args()
	createAnimation(project_dir, args.airportCode, args.outputDir, logger)
