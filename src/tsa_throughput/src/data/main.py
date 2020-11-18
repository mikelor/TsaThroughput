#packages
import json
import pandas
from pandas import json_normalize

#load json file
with open(r"c:\users\skaran\repos\tsathroughput\data\tsathroughput.json") as f:
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
print(df)

#export normalized JSON to CSV file
csv_export = df.to_csv(r"c:\users\skaran\repos\tsathroughput\data\tsathroughputsmall.csv", index=False)