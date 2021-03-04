#packages
import json
import os
import pandas
from pandas import json_normalize
import argparse

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

#print(df)
#print(df.shape)

#New dataframe with limited columns
df2 = df.reindex(columns= ['Airports.Days.Date','Hour','Airports.AirportCode','Airports.AirportName','Airports.City','Airports.State','Amount'])
print(df2)

#Filter only SEA
isSea = df['Airports.AirportCode'] == 'SEA'
#print(isSea.head())

#Create data frame with only SEA
df_sea = df[isSea]
#print(df_sea.shape)

#export normalized JSON to CSV file
#csv_export = df_pivot.to_csv(outputFile, index=False)
