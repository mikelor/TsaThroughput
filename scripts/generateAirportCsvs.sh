#!/bin/bash

# This script automates the generation of individual CSV files for each airport.

# Navigate to the directory containing the JSON data files
cd ../data/raw/tsa/throughput

# Extract airport codes from the JSON files
airport_codes=$(jq -r '.Airports[].AirportCode' *.json | sort -u)

# Iterate over each airport code and generate a CSV file using the cvtJsonToCsv.sh script
for code in $airport_codes
do
    echo "Generating CSV for airport code: $code"
    ../scripts/cvtJsonToCsv.sh -a $code
done

echo "CSV generation for all airports completed."

# Navigate back to the scripts directory
cd ../../../scripts
