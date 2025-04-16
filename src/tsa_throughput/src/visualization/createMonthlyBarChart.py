import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import logging
from dotenv import find_dotenv, load_dotenv
from argparse import ArgumentParser

from pathlib import Path

def loadAndPlotAirports(airports, logger):
    # Load the file into a dataframe and checkout the structure
    # Make sure you run this file from the project root folder
    projectDir = Path('.').resolve()
    print(projectDir)

    for airport in airports:
        processTsaThroughput(airport, f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.{airport}.csv')

def processTsaThroughput(airport, filepath):
    """
    Reads a CSV file, calculates daily throughput, and creates a line graph, one line per year.

    Args:
        filepath: The path to the CSV file.

    Returns:
        None. Displays the graph. Prints informative error messages.
    """
    projectDir = Path('.').resolve()

    try:
        # Read the CSV file.
        df = pd.read_csv(filepath)

        # Convert 'Date' column to datetime objects. Handle potential errors.
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except Exception as e:
            print(f"Error converting 'Date' column to datetime: {e}")
            return

        # Calculate daily throughput (sum of all LAS terminals for each hour).
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns  # Get numeric columns
            df['DailyThroughput'] = df[numeric_cols].sum(axis=1)  # Sum only numeric cols
        except KeyError as e:
            print(f"Error: One or more TSA throughput columns are missing from the CSV. Check for typos in column names: {e}")
            return

        # Extract the year and format the date as Month numbers (MM).
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.strftime('%m')  # Extract month as a number

        # Calculate total throughput for each month of each year.
        monthly_throughput = df.groupby(['Year', 'Month'])['DailyThroughput'].sum().unstack(0)

        # Prepare data for clustering
        months = monthly_throughput.index
        num_months = len(months)
        num_years = len(monthly_throughput.columns)
        bar_width = 0.5  #Width is now for group of years
        group_gap = 0.1
        individual_bar_width = (bar_width - (num_years * group_gap)) / num_years
        group_positions = np.arange(num_months) # Positions for each month group


        fig, ax = plt.subplots(figsize=(15, 7))

        # Create clustered bar chart
        for i, year in enumerate(monthly_throughput.columns):
            offset = group_gap * (i - (num_years - 1) / 2) #Offset is now just the group gap
            x_pos = group_positions + offset
            ax.bar(x_pos, monthly_throughput[year].fillna(0), width=individual_bar_width, label=str(year))

        # Customize the chart
        ax.set_xlabel('Month')
        ax.set_ylabel('Throughput')
        ax.set_title(f'TSA Throughput for {airport}')
        ax.set_xticks(group_positions) # Set the x ticks at the group positions

        # Create a list of month labels from numbers to names:
        month_labels = [pd.to_datetime(f'{month}/01', format='%m/%d').strftime('%b') for month in months]
        ax.set_xticklabels(month_labels, rotation=45, ha='right')

        ax.legend(title='Year')
        fig.tight_layout() #Avoid overlapping elements

        plt.grid(axis='y') #Y-axis grid

        plt.savefig(f'{projectDir}/src/tsa_throughput/src/visualization/figures/Figure.MonthlyBarChart.{airport}.png')
        plt.close(fig)
    

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


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
    loadAndPlotAirports(airports, logger)

    logger.info('Finished making final data set from raw data.')
