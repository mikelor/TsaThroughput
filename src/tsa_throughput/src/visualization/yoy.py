import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Read the CSV file into a Pandas DataFrame
# Load the file into a dataframe and checkout the structure
# Make sure you run this file from the project root folder
projectDir = Path('.').resolve()
data = pd.read_csv(f'{projectDir}/data/processed/tsa/throughput/TsaThroughput.Total.csv')

# Extract the year from the 'Date' column and create a new column
data['Year'] = pd.DatetimeIndex(data['Date']).year

# Group the data by year and calculate the total throughput for each year
yearly_throughput = data.groupby('Year')['All'].sum()

# Create the chart
plt.figure(figsize=(12, 6))  # Adjust figure size as needed
plt.plot(yearly_throughput.index, yearly_throughput.values)
plt.xlabel("Year")
plt.ylabel("Total Throughput")
plt.title("TSA Yearly Throughput")
plt.grid(True)
plt.savefig(f'{projectDir}/src/tsa_throughput/src/visualization/figures/Figure.YOY.png')
plt.close()