echo $1
#./cvtPdfToJson.sh $1
python ../src/tsa_throughput/src/data/make_airport_dataset.py file -f ../data/raw/tsa/throughput/$1 -o ../data/processed/tsa/throughput/
./processJsonToCsv.sh
./createFigures.sh