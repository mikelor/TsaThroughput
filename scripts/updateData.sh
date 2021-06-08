echo $1
./cvtPdfToJson.sh $1
./processJsonToCsv.sh
./createFigures.sh