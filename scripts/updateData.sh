echo $1
./cvtPdfToJson.sh $1
./cvtJsonToCsv.sh $1
./createAirportCsvs.sh
./createAirportFigures.sh