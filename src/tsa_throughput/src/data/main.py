#packages
import json
import pandas
from pandas import json_normalize

#load json file
with open(r"../../../../data/tsa-throughput-november-22-2020-to-november-28-2020.json") as f:
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
# Convert to datetime and get time
df['Hour'] = pandas.to_datetime(df['Hour'], errors='coerce')
df['Hour'] = df['Hour'].dt.time

#Convert to datetime and get date
df['Airports.Days.Date'] = pandas.to_datetime(df['Airports.Days.Date'], errors='coerce')
df['Airports.Days.Date'].dt.date

#print(df)
#print(df.shape)

#Filter only SEA
isSea = df['Airports.AirportCode'] == 'SEA'
#print(isSea.head())

#Create data frame with only SEA
df_sea = df[isSea]
#print(df_sea.shape)

#Create pivot table
df_pivot = df_sea.pivot_table(index=['Airports.Days.Date','Hour'], columns=['Airports.AirportCode','Airports.Days.Checkpoints.CheckpointName'], values='Amount').reset_index()
print(df_pivot)

#export normalized JSON to CSV file
csv_export = df_pivot.to_csv(r"../../../../data/tsathroughoutpivot.csv", index=False)
