#packages
import json
import pandas
from pandas import json_normalize

#load json file
with open(r"c:\users\skaran\repos\tsathroughput\data\tsathroughput.json") as f:
  data = json.load(f)

#normalize json
df = json_normalize(data)

#export normalized JSON to CSV file
csv_export = df.to_csv('tsathroughputsmall.csv', index=False)