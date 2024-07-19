echo "Ensure X Windows is configured for graphics.
cmd.exe /c c:/tmp/xsrv.bat

echo "Extracting airport codes from JSON files"
# Navigate to the directory containing the JSON data files
cd ../data/raw/tsa/throughput

# Extract airport codes from the JSON files
airport_codes=$(jq -r '.Airports[].AirportCode' *.json | sort -u)

# Navigate back to the porject directory
cd ../../../..
python src/tsa_throughput/src/visualization/createFigures.py -a "$airport_codes"
cd scripts