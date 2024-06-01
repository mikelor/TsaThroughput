# This script now dynamically generates CSV files for all airports listed in the JSON data.
# It iterates over all airport codes in the JSON files and generates CSV files for each airport code found.

# Navigate to the directory containing the JSON data files
cd ../data/raw/tsa/throughput

# Loop through all JSON files in the directory
for file in *.json
do
    # Extract airport codes from the JSON file
    airport_codes=$(jq '.Airports[].AirportCode' $file | sort | uniq | tr -d '"')

    # For each airport code, generate a CSV file using the make_airport_dataset.py script
    for code in $airport_codes
    do
        echo "Generating CSV for airport code: $code"
        python ../../src/tsa_throughput/src/data/make_airport_dataset.py file -f $file -a $code -o ../../data/processed/tsa/throughput/
    done
done

# Navigate back to the scripts directory
cd ../../../scripts
