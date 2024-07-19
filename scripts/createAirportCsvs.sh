
echo "Building cache file for all airports."
python ../src/tsa_throughput/src/data/make_airport_dataset.py dir -d ../data/raw/tsa/throughput  -o ../data/processed/tsa/throughput
echo "Cache file built."


echo "Extracting airport codes from JSON files"
# Navigate to the directory containing the JSON data files
cd ../data/raw/tsa/throughput

# Extract airport codes from the JSON files
airport_codes=$(jq -r '.Airports[].AirportCode' *.json | sort -u)

# Navigate back to the scripts directory
cd ../../../../scripts

# Iterate over each airport code and generate a CSV file using the cvtJsonToCsv.sh script
echo "Generating CSV for airport code: $airport_codes"
python ../src/tsa_throughput/src/data/make_airport_dataset.py csv -f ../data/processed/tsa/throughput/TsaThroughput.Cache.csv -a "$airport_codes" -o ../data/processed/tsa/throughput 
    
echo "CSV generation for all airports completed."



 
