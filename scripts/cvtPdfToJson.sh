echo $1
justName="$(basename -s .pdf ${1})"
echo $justName
dotnet run --project ../src/TsaThroughputApp/ ../data/${justName}.pdf ../data/raw/tsa/throughput/${justName}.json
